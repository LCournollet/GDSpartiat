"""Theme based on the Geometry Dash menus."""

import tkinter as tk
from tkinter import font as tkfont, ttk

BG = "#0a2a7a"
PANEL = "#123a9c"
FIELD = "#061845"
TEXT = "#ffffff"
MUTED = "#9fc3ff"
YELLOW = "#ffd21f"
GREEN = "#5ee03a"
GREEN_HI = "#86f25c"
YELLOW_HI = "#ffe468"
OUTLINE = "#000000"
GRAD_TOP = "#00b4ff"
GRAD_BOTTOM = "#0a2a7a"


def pick_font(root, *names):
    available = set(tkfont.families(root))
    for name in names:
        if name in available:
            return name
    return "TkDefaultFont"


def apply(root):
    title_font = pick_font(root, "Pusab", "Arial Black", "Impact", "Segoe UI Black")
    body_font = pick_font(root, "Segoe UI Semibold", "Segoe UI", "Arial")
    root.title_font = title_font
    root.configure(bg=BG)
    root.option_add("*TCombobox*Listbox*Background", FIELD)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=PANEL, foreground=TEXT, font=(body_font, 10),
                    bordercolor=OUTLINE, lightcolor=PANEL, darkcolor=PANEL, focuscolor=YELLOW)
    style.configure("TFrame", background=PANEL)
    style.configure("Bg.TFrame", background=BG)
    style.configure("TLabel", background=PANEL, foreground=TEXT, font=(body_font, 10, "bold"))
    style.configure("Bg.TLabel", background=BG, foreground=MUTED, font=(body_font, 9))
    style.configure("Value.TLabel", background=PANEL, foreground=MUTED, font=(body_font, 9))

    style.configure("TEntry", fieldbackground=FIELD, foreground=YELLOW, insertcolor=TEXT,
                    bordercolor=OUTLINE, lightcolor=FIELD, darkcolor=FIELD, padding=4)
    style.map("TEntry", bordercolor=[("focus", YELLOW)], lightcolor=[("focus", YELLOW)],
              fieldbackground=[("readonly", PANEL)], foreground=[("readonly", MUTED)])

    for name, color, hi in (("TButton", GREEN, GREEN_HI), ("Save.TButton", YELLOW, YELLOW_HI)):
        style.configure(name, background=color, foreground=OUTLINE, font=(title_font, 10),
                        bordercolor=OUTLINE, lightcolor=hi, darkcolor=color, borderwidth=3,
                        padding=(14, 6), relief="raised")
        style.map(name, background=[("pressed", color), ("active", hi)],
                  relief=[("pressed", "sunken")])

    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(6, 6, 6, 0))
    style.configure("TNotebook.Tab", background="#1b4fc7", foreground=TEXT, font=(title_font, 10),
                    padding=(14, 6), bordercolor=OUTLINE, lightcolor="#2a64e0", darkcolor="#1b4fc7")
    style.map("TNotebook.Tab",
              background=[("selected", YELLOW), ("active", "#2a64e0")],
              foreground=[("selected", OUTLINE)],
              expand=[("selected", (2, 2, 2, 0))])

    style.configure("Treeview", background=FIELD, fieldbackground=FIELD, foreground=TEXT,
                    rowheight=24, bordercolor=OUTLINE, font=(body_font, 10))
    style.map("Treeview", background=[("selected", YELLOW)], foreground=[("selected", OUTLINE)])
    style.configure("Treeview.Heading", background=GREEN, foreground=OUTLINE, font=(title_font, 9),
                    bordercolor=OUTLINE, relief="raised")
    style.map("Treeview.Heading", background=[("active", GREEN_HI)])
    style.configure("Vertical.TScrollbar", background=YELLOW, troughcolor=FIELD,
                    bordercolor=OUTLINE, arrowcolor=OUTLINE, lightcolor=YELLOW, darkcolor=YELLOW)
    style.configure("Group.TLabelframe", background=PANEL, bordercolor=OUTLINE, borderwidth=2,
                    lightcolor=PANEL, darkcolor=PANEL)
    style.configure("Group.TLabelframe.Label", background=PANEL, foreground=YELLOW, font=(title_font, 10))


def _mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


class Header(tk.Canvas):
    """Gradient banner with a yellow title outlined in black."""

    def __init__(self, master, title, subtitle=""):
        super().__init__(master, height=78, highlightthickness=0, bg=BG)
        self.title = title
        self.subtitle = subtitle
        self.font = getattr(master, "title_font", "TkDefaultFont")
        self.bind("<Configure>", lambda _e: self.draw())

    def outlined(self, x, y, text, size, fill, anchor="w", width=2):
        f = (self.font, size)
        for dx in range(-width, width + 1):
            for dy in range(-width, width + 1):
                if dx or dy:
                    self.create_text(x + dx, y + dy, text=text, font=f, fill=OUTLINE, anchor=anchor)
        self.create_text(x, y, text=text, font=f, fill=fill, anchor=anchor)

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        for y in range(h):
            self.create_line(0, y, w, y, fill=_mix(GRAD_TOP, GRAD_BOTTOM, y / max(h - 1, 1)))
        # small squares in the background, like the menu decorations
        for i, x in enumerate(range(w - 260, w, 52)):
            s = 30 if i % 2 else 22
            yy = 16 if i % 2 else 34
            self.create_rectangle(x, yy, x + s, yy + s, outline="#4fd0ff", width=2)
        self.outlined(20, 34, self.title, 26, YELLOW, width=3)
        if self.subtitle:
            self.outlined(22, 64, self.subtitle, 9, TEXT, width=1)
        self.create_line(0, h - 2, w, h - 2, fill=OUTLINE, width=3)
