import ctypes
import os
import tkinter as tk
from ctypes import wintypes
from tkinter import ttk, filedialog, messagebox, simpledialog

import gdsave
import theme

APP_NAME = "GDSpartiat"

# GS_value keys (player stats), grouped.
# Each field: (key, label, symbol, color)
STATS = [
    ("Collectibles", [
        ("6", "Stars", "★", "#ffd21f"),
        ("28", "Moons", "☾", "#c8e6ff"),
        ("13", "Diamonds", "◆", "#5ff2ff"),
        ("29", "Diamonds (total)", "◆", "#5ff2ff"),
        ("14", "Orbs (shop)", "●", "#4fe0ff"),
        ("22", "Orbs (total)", "●", "#4fe0ff"),
        ("21", "Demon keys", "✦", "#ff9a3c"),
        ("8", "Secret coins", "◉", "#ffd21f"),
        ("12", "User coins", "◉", "#d9d9d9"),
    ]),
    ("Progression", [
        ("5", "Demons", "☠", "#ff4d4d"),
        ("3", "Official levels", "■", "#5ee03a"),
        ("4", "Online levels", "■", "#5ee03a"),
        ("15", "Dailies", "▲", "#ffd21f"),
        ("40", "Gauntlets", "▲", "#ff9a3c"),
        ("7", "Map packs", "■", "#c58bff"),
    ]),
    ("Activity", [
        ("1", "Jumps", "▲", "#ffffff"),
        ("2", "Attempts", "↻", "#ffffff"),
        ("9", "Players destroyed", "✖", "#ff4d4d"),
        ("10", "Liked levels", "♥", "#ff6fb0"),
        ("11", "Rated levels", "★", "#ffffff"),
    ]),
    ("Shards", [
        ("16", "Fire", "◆", "#ff6a2a"),
        ("17", "Ice", "◆", "#8ee8ff"),
        ("18", "Poison", "◆", "#7dff4a"),
        ("19", "Shadow", "◆", "#a070ff"),
        ("20", "Lava", "◆", "#ff3a2a"),
        ("23", "Earth", "◆", "#c08a4a"),
        ("24", "Blood", "◆", "#c0102a"),
        ("25", "Metal", "◆", "#c8c8c8"),
        ("26", "Light", "◆", "#fff6a0"),
        ("27", "Soul", "◆", "#ff8ad8"),
    ]),
]

PLAYER = [
    ("Profile", [
        ("playerName", "Username", "☺", "#ffd21f"),
    ]),
    ("Icons", [
        ("playerFrame", "Cube", "■", "#5ee03a"),
        ("playerShip", "Ship", "▶", "#5ee03a"),
        ("playerBall", "Ball", "●", "#5ee03a"),
        ("playerBird", "UFO", "◒", "#5ee03a"),
        ("playerDart", "Wave", "▸", "#5ee03a"),
        ("playerRobot", "Robot", "▣", "#5ee03a"),
        ("playerSpider", "Spider", "✳", "#5ee03a"),
        ("playerSwing", "Swing", "◈", "#5ee03a"),
        ("playerJetpack", "Jetpack", "▲", "#5ee03a"),
    ]),
    ("Colors and effects", [
        ("playerColor", "Color 1", "■", "#ffd21f"),
        ("playerColor2", "Color 2", "■", "#4fe0ff"),
        ("playerColor3", "Glow color", "■", "#ffffff"),
        ("playerStreak", "Trail", "━", "#ffffff"),
        ("playerShipStreak", "Ship trail", "━", "#ffffff"),
        ("playerDeathEffect", "Death effect", "✸", "#ff4d4d"),
    ]),
]


class FieldGrid(ttk.Frame):
    """Label / value fields arranged in boxes, bound to a list of keys."""

    def __init__(self, master, groups, columns=2):
        super().__init__(master, padding=12)
        self.fields = [(f[0], f[1]) for _, fields in groups for f in fields]
        self.vars = {}
        for i, (title, fields) in enumerate(groups):
            box = ttk.LabelFrame(self, text=f" {title} ", style="Group.TLabelframe", padding=(10, 6))
            box.grid(row=i // columns, column=i % columns, sticky="nsew", padx=6, pady=6)
            per = -(-len(fields) // 2) if len(fields) > 6 else len(fields)
            for n, (key, label, glyph, color) in enumerate(fields):
                row, col = n % per, (n // per) * 3
                tk.Label(box, text=glyph, fg=color, bg=theme.PANEL,
                         font=("Segoe UI Symbol", 12)).grid(row=row, column=col, padx=(8 if col else 0, 6))
                ttk.Label(box, text=label).grid(row=row, column=col + 1, sticky="w", padx=(0, 10), pady=2)
                var = tk.StringVar()
                ttk.Entry(box, textvariable=var, width=12, font=("Segoe UI Semibold", 11)).grid(row=row, column=col + 2, sticky="e", pady=2)
                self.vars[key] = var
        for c in range(columns):
            self.columnconfigure(c, weight=1)

    def load(self, pdict):
        for key, var in self.vars.items():
            value = pdict.get(key, "") if pdict else ""
            var.set(value if isinstance(value, str) else "")

    def changed(self, pdict):
        for key, var in self.vars.items():
            old = pdict.get(key) if pdict else None
            old = old if isinstance(old, str) else ""
            if var.get().strip() != old:
                return True
        return False

    def apply(self, pdict, numeric=True):
        for key, label in self.fields:
            value = self.vars[key].get().strip()
            old = pdict.get(key)
            if value == "" and old is None:
                continue
            if numeric and key != "playerName":
                try:
                    int(value)
                except ValueError:
                    raise ValueError(f"{label} : '{value}' is not a whole number")
            if value != old:
                pdict.set(key, value)


class KeyTable(ttk.Frame):
    """Editable table of every simple value in a dictionary."""

    def __init__(self, master, on_change=None, before_change=None):
        super().__init__(master, padding=10)
        self.pdict = None
        self.on_change = on_change or (lambda: None)
        self.before_change = before_change or (lambda: True)
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 6))
        ttk.Label(bar, text="Filter:").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(bar, textvariable=self.filter_var, width=30).pack(side="left", padx=6)
        ttk.Button(bar, text="Add key", command=self.add_key).pack(side="right")
        ttk.Label(bar, text="Double-click to edit").pack(side="right", padx=10)

        self.tree = ttk.Treeview(self, columns=("key", "type", "value"), show="headings")
        self.tree.heading("key", text="Key")
        self.tree.heading("type", text="Type")
        self.tree.heading("value", text="Value")
        self.tree.column("key", width=200)
        self.tree.column("type", width=50, anchor="center")
        self.tree.column("value", width=450)
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.edit_selected)

    def load(self, pdict):
        self.pdict = pdict
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        if self.pdict is None:
            return
        flt = self.filter_var.get().lower()
        for key in self.pdict.keys():
            elem = self.pdict.raw(key)
            if elem.tag == "d":
                continue
            value = "true" if elem.tag == "t" else (elem.text or "")
            if flt and flt not in key.lower() and flt not in value.lower():
                continue
            shown = value if len(value) < 300 else value[:300] + "..."
            self.tree.insert("", "end", iid=key, values=(key, elem.tag, shown))

    def edit_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel or self.pdict is None:
            return
        key = sel[0]
        elem = self.pdict.raw(key)
        if elem.tag == "t":
            messagebox.showinfo(APP_NAME, "Boolean value, nothing to edit.")
            return
        value = simpledialog.askstring(APP_NAME, f"New value for {key}:", initialvalue=elem.text or "", parent=self)
        if value is not None and self.before_change():
            self.pdict.set(key, value)
            self.refresh()
            self.on_change()

    def add_key(self):
        if self.pdict is None:
            return
        key = simpledialog.askstring(APP_NAME, "Key name:", parent=self)
        if not key:
            return
        value = simpledialog.askstring(APP_NAME, f"Value for {key}:", parent=self)
        if value is None or not self.before_change():
            return
        self.pdict.set(key, value)
        self.refresh()
        self.on_change()



class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_wchar * 260),
    ]


def running_processes():
    """Names of running processes, read through the Windows API (no console spawned)."""
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    snap = kernel32.CreateToolhelp32Snapshot(0x2, 0)
    if not snap or snap == wintypes.HANDLE(-1).value:
        raise OSError("CreateToolhelp32Snapshot failed")
    names = set()
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(entry)
    try:
        ok = kernel32.Process32FirstW(snap, ctypes.byref(entry))
        while ok:
            names.add(entry.szExeFile.lower())
            ok = kernel32.Process32NextW(snap, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snap)
    return names


def gd_is_running():
    """True if the game is running, None if it cannot be determined."""
    try:
        return "geometrydash.exe" in running_processes()
    except Exception:
        return None


class App(tk.Tk):
    def __init__(self, autoload=True):
        super().__init__()
        theme.apply(self)
        self.title(APP_NAME)
        self.geometry("960x740")
        self.minsize(700, 450)
        self.save = None
        self.dirty = False

        menu = tk.Menu(self)
        fmenu = tk.Menu(menu, tearoff=0)
        fmenu.add_command(label="Open CCGameManager.dat", command=self.open_default)
        fmenu.add_command(label="Open file...", command=self.open_other)
        fmenu.add_separator()
        fmenu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        fmenu.add_command(label="Save as...", command=self.save_as)
        fmenu.add_separator()
        fmenu.add_command(label="Export to XML...", command=self.export_xml)
        fmenu.add_command(label="Import XML...", command=self.import_xml)
        fmenu.add_separator()
        fmenu.add_command(label="Restore .bak backup", command=self.restore_backup)
        fmenu.add_separator()
        fmenu.add_command(label="Quit", command=self.on_close)
        menu.add_cascade(label="File", menu=fmenu)
        self.config(menu=menu)
        self.bind("<Control-s>", lambda _e: self.save_file())
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        theme.Header(self, APP_NAME, "Geometry Dash save editor").pack(side="top", fill="x")

        bottom = ttk.Frame(self, padding=(12, 8), style="Bg.TFrame")
        bottom.pack(side="bottom", fill="x")
        ttk.Button(bottom, text="Save", style="Save.TButton", command=self.save_file).pack(side="right")
        ttk.Button(bottom, text="Discard changes", command=self.reload).pack(side="right", padx=6)
        self.status = tk.StringVar(value="No file open")
        ttk.Label(bottom, textvariable=self.status, anchor="w", style="Bg.TLabel").pack(side="left", fill="x", expand=True)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=6, pady=6)
        self.tabs.bind("<<NotebookTabChanged>>", lambda _e: self.sync_fields())

        self.stats = FieldGrid(self.tabs, STATS, columns=2)
        self.tabs.add(self.stats, text="Stats")

        self.player = FieldGrid(self.tabs, PLAYER, columns=3)
        self.tabs.add(self.player, text="Player")

        self.values_table = KeyTable(self.tabs, on_change=self.on_table_change, before_change=self.sync_fields)
        self.tabs.add(self.values_table, text="All stats (GS_value)")

        self.root_table = KeyTable(self.tabs, on_change=self.on_table_change, before_change=self.sync_fields)
        self.tabs.add(self.root_table, text="Settings and misc")

        if autoload:
            self.after(100, self.open_default)

    # Files

    def load(self, path):
        try:
            self.save = gdsave.SaveFile(path)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not read {path}\n\n{e}")
            return
        self.dirty = False
        self.refresh_all()
        self.status.set(path)
        if gd_is_running():
            self.status.set("Geometry Dash is running: close it before saving, or your changes will be lost")
            messagebox.showwarning(
                APP_NAME,
                "Geometry Dash is running.\n\n"
                "Close the game first: it overwrites the save when it exits.",
            )

    def reload(self):
        if self.save is not None:
            self.load(self.save.path)

    def refresh_all(self):
        data = self.save.data
        gs = data.get("GS_value")
        self.stats.load(gs)
        self.player.load(data)
        self.values_table.load(gs)
        self.root_table.load(data)

    def has_changes(self):
        if self.save is None:
            return False
        data = self.save.data
        return self.dirty or self.stats.changed(data.get("GS_value")) or self.player.changed(data)

    def open_default(self):
        path = os.path.join(gdsave.default_save_dir(), "CCGameManager.dat")
        if os.path.exists(path):
            self.load(path)
        else:
            self.open_other()

    def open_other(self):
        path = filedialog.askopenfilename(
            initialdir=gdsave.default_save_dir(),
            filetypes=[("GD save", "*.dat"), ("All files", "*.*")],
        )
        if path:
            self.load(path)

    def check_open(self):
        if self.save is None:
            messagebox.showwarning(APP_NAME, "No file open.")
            return False
        return True

    def sync_fields(self):
        """Copy the field values into the save held in memory."""
        if self.save is None:
            return True
        data = self.save.data
        try:
            if self.stats.changed(data.get("GS_value")):
                self.stats.apply(data.ensure_dict("GS_value"))
                self.dirty = True
            if self.player.changed(data):
                self.player.apply(data)
                self.dirty = True
        except ValueError as e:
            messagebox.showerror(APP_NAME, str(e))
            return False
        self.refresh_all()
        return True

    def save_file(self, path=None):
        if not self.check_open():
            return False
        if not self.sync_fields():
            return False
        running = gd_is_running()
        if running:
            messagebox.showwarning(
                APP_NAME,
                "Geometry Dash is running and will overwrite the save when it closes.\n\n"
                "Close the game, then save again.",
            )
            return False
        if running is None and not messagebox.askyesno(
            APP_NAME,
            "Could not check whether Geometry Dash is running.\n\n"
            "Make sure the game is closed. Save now?",
        ):
            return False
        target = path or self.save.path
        try:
            self.save.save(path)
            if gdsave.SaveFile(target).to_xml() != self.save.to_xml():
                raise IOError("the file read back does not match")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Save failed\n\n{e}")
            return False
        self.dirty = False
        self.status.set(f"Saved and verified: {target} (previous file copied to .bak)")
        return True

    def save_as(self):
        if not self.check_open():
            return
        path = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("GD save", "*.dat")])
        if path:
            self.save_file(path)

    def export_xml(self):
        if not self.check_open() or not self.sync_fields():
            return
        path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML", "*.xml")])
        if path:
            with open(path, "wb") as f:
                f.write(self.save.to_xml())
            self.status.set(f"XML exported: {path}")

    def import_xml(self):
        if not self.check_open():
            return
        path = filedialog.askopenfilename(filetypes=[("XML", "*.xml"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "rb") as f:
                self.save.set_xml(f.read())
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Invalid XML\n\n{e}")
            return
        self.dirty = True
        self.refresh_all()
        self.status.set(f"XML imported from {path} (not saved yet)")

    def restore_backup(self):
        if not self.check_open():
            return
        backup = self.save.path + ".bak"
        if not os.path.exists(backup):
            messagebox.showinfo(APP_NAME, "No .bak file found.")
            return
        if messagebox.askyesno(APP_NAME, f"Replace the current file with\n{backup}?"):
            with open(backup, "rb") as src, open(self.save.path, "wb") as dst:
                dst.write(src.read())
            self.load(self.save.path)

    def on_table_change(self):
        self.dirty = True
        self.refresh_all()
        self.status.set("Modified (not saved yet)")

    def on_close(self):
        if self.has_changes():
            answer = messagebox.askyesnocancel(APP_NAME, "You have unsaved changes.\n\nSave before quitting?")
            if answer is None:
                return
            if answer and not self.save_file():
                return
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
