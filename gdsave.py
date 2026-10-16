"""Read and write Geometry Dash save files (Windows version).

Format: XOR 11 -> urlsafe base64 -> gzip -> RobTop's own plist XML.
"""

import base64
import gzip
import os
import zlib
import xml.etree.ElementTree as ET

XOR_KEY = 11


def default_save_dir():
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "GeometryDash")


def decode_bytes(raw):
    raw = raw.rstrip(b"\x00")
    if raw.lstrip().startswith(b"<?xml"):
        return raw
    data = bytes(b ^ XOR_KEY for b in raw)
    data = data.replace(b"\x00", b"").rstrip(b"\x0b").strip()
    data += b"=" * (-len(data) % 4)
    data = base64.urlsafe_b64decode(data)
    return zlib.decompress(data, 15 | 32)


def encode_bytes(xml):
    data = gzip.compress(xml)
    data = base64.urlsafe_b64encode(data)
    return bytes(b ^ XOR_KEY for b in data)


def read_xml(path):
    with open(path, "rb") as f:
        return decode_bytes(f.read())


def write_xml(path, xml):
    with open(path, "wb") as f:
        f.write(encode_bytes(xml))


class PlistDict:
    """View over a <d> element: each <k> key is followed by its value."""

    def __init__(self, elem):
        self.elem = elem

    def _pairs(self):
        children = list(self.elem)
        for i in range(0, len(children) - 1, 2):
            if children[i].tag == "k":
                yield children[i], children[i + 1]

    def keys(self):
        return [k.text or "" for k, _ in self._pairs()]

    def raw(self, key):
        for k, v in self._pairs():
            if k.text == key:
                return v
        return None

    def get(self, key, default=None):
        v = self.raw(key)
        if v is None:
            return default
        if v.tag == "t":
            return True
        if v.tag == "d":
            return PlistDict(v)
        return v.text or ""

    def set(self, key, value, tag=None):
        v = self.raw(key)
        if tag is None:
            if v is not None and v.tag in ("s", "i", "r"):
                tag = v.tag
            else:
                tag = "s"
        if v is None:
            k = ET.SubElement(self.elem, "k")
            k.text = key
            v = ET.SubElement(self.elem, tag)
        else:
            v.tag = tag
            v.clear()
        v.text = str(value)

    def ensure_dict(self, key):
        v = self.raw(key)
        if v is None:
            k = ET.SubElement(self.elem, "k")
            k.text = key
            v = ET.SubElement(self.elem, "d")
        return PlistDict(v)


def file_stamp(path):
    st = os.stat(path)
    return st.st_mtime_ns, st.st_size


class SaveFile:
    def __init__(self, path):
        self.path = path
        self.stamp = file_stamp(path)
        xml = read_xml(path)
        self.root = ET.fromstring(xml)
        self.data = PlistDict(self.root.find("dict"))

    def to_xml(self):
        body = ET.tostring(self.root, encoding="unicode")
        return ('<?xml version="1.0"?>' + body).encode("utf-8")

    def set_xml(self, xml):
        self.root = ET.fromstring(xml)
        self.data = PlistDict(self.root.find("dict"))

    def disk_changed(self):
        """True if something (usually the game) rewrote the file since it was read."""
        try:
            return file_stamp(self.path) != self.stamp
        except OSError:
            return False

    def save(self, path=None):
        path = path or self.path
        if os.path.exists(path):
            backup = path + ".bak"
            with open(path, "rb") as src, open(backup, "wb") as dst:
                dst.write(src.read())
        write_xml(path, self.to_xml())
        if path == self.path:
            self.stamp = file_stamp(path)


# Reward types used in chests (GJRewardObject key 1)
REWARD_TYPES = {
    1: "Fire shards",
    2: "Ice shards",
    3: "Poison shards",
    4: "Shadow shards",
    5: "Lava shards",
    6: "Demon keys",
    7: "Orbs",
    8: "Diamonds",
    10: "Earth shards",
    11: "Blood shards",
    12: "Metal shards",
    13: "Light shards",
    14: "Soul shards",
    15: "Gold keys",
}


def _int_node(parent, key, value):
    k = ET.SubElement(parent, "k")
    k.text = key
    v = ET.SubElement(parent, "i")
    v.text = str(value)


def add_chest(save, rewards):
    """Add an opened timed chest holding the given rewards {type: amount}.

    In 2.2 the game rebuilds orbs, diamonds, shards and keys from opened
    chests at launch, so this is the way to change them.
    """
    rewards = {t: int(a) for t, a in rewards.items() if int(a) > 0}
    if not rewards:
        return None
    chests = save.data.ensure_dict("GS_11")
    ids = [int(k[2:]) for k in chests.keys() if k.startswith("1_") and k[2:].isdigit()]
    chest_id = max(ids, default=0) + 1
    key = f"1_{chest_id}"

    k = ET.SubElement(chests.elem, "k")
    k.text = key
    chest = ET.SubElement(chests.elem, "d")
    _int_node(chest, "kCEK", 8)
    _int_node(chest, "1", chest_id)
    _int_node(chest, "2", 1)
    k = ET.SubElement(chest, "k")
    k.text = "3"
    items = ET.SubElement(chest, "d")
    k = ET.SubElement(items, "k")
    k.text = "_isArr"
    ET.SubElement(items, "t")
    for n, (rtype, amount) in enumerate(sorted(rewards.items())):
        k = ET.SubElement(items, "k")
        k.text = f"k_{n}"
        item = ET.SubElement(items, "d")
        _int_node(item, "kCEK", 9)
        _int_node(item, "1", rtype)
        _int_node(item, "3", amount)
    return key


def chest_totals(save):
    """Sum of every chest reward in the save, by reward type."""
    totals = {}

    def walk(elem):
        kids = list(elem)
        pairs = {kids[i].text: kids[i + 1] for i in range(0, len(kids) - 1, 2) if kids[i].tag == "k"}
        if pairs.get("kCEK") is not None and pairs["kCEK"].text == "9":
            t, a = pairs.get("1"), pairs.get("3")
            if t is not None and a is not None:
                totals[int(t.text)] = totals.get(int(t.text), 0) + int(a.text)
        for child in elem:
            if child.tag == "d":
                walk(child)

    for key in save.data.keys():
        elem = save.data.raw(key)
        if key.startswith("GS_") and elem.tag == "d":
            walk(elem)
    return totals
