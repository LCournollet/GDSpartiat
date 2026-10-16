"""Lecture et ecriture des fichiers de sauvegarde Geometry Dash (version Windows).

Format : XOR 11 -> base64 urlsafe -> gzip -> plist XML maison de RobTop.
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
    """Vue sur un element <d> : les cles <k> sont suivies de leur valeur."""

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


class SaveFile:
    def __init__(self, path):
        self.path = path
        xml = read_xml(path)
        self.root = ET.fromstring(xml)
        self.data = PlistDict(self.root.find("dict"))

    def to_xml(self):
        body = ET.tostring(self.root, encoding="unicode")
        return ('<?xml version="1.0"?>' + body).encode("utf-8")

    def set_xml(self, xml):
        self.root = ET.fromstring(xml)
        self.data = PlistDict(self.root.find("dict"))

    def save(self, path=None):
        path = path or self.path
        if os.path.exists(path):
            backup = path + ".bak"
            with open(path, "rb") as src, open(backup, "wb") as dst:
                dst.write(src.read())
        write_xml(path, self.to_xml())
