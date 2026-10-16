import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import gdsave

APP_NAME = "GDSpartiat"

# Cles de GS_value (statistiques du joueur)
STATS = [
    ("6", "Etoiles"),
    ("28", "Lunes"),
    ("13", "Diamants"),
    ("29", "Diamants (total)"),
    ("14", "Orbes"),
    ("22", "Orbes (total)"),
    ("21", "Cles demon"),
    ("8", "Secret coins"),
    ("12", "User coins"),
    ("5", "Demons completes"),
    ("3", "Niveaux officiels completes"),
    ("4", "Niveaux en ligne completes"),
    ("15", "Dailies completes"),
    ("40", "Gauntlets completes"),
    ("7", "Map packs completes"),
    ("1", "Sauts"),
    ("2", "Tentatives"),
    ("9", "Joueurs detruits"),
    ("10", "Niveaux likes"),
    ("11", "Niveaux notes"),
    ("16", "Shards feu"),
    ("17", "Shards glace"),
    ("18", "Shards poison"),
    ("19", "Shards ombre"),
    ("20", "Shards lave"),
    ("23", "Shards terre"),
    ("24", "Shards sang"),
    ("25", "Shards metal"),
    ("26", "Shards lumiere"),
    ("27", "Shards ame"),
]

PLAYER = [
    ("playerName", "Pseudo"),
    ("playerFrame", "Cube"),
    ("playerShip", "Vaisseau"),
    ("playerBall", "Boule"),
    ("playerBird", "UFO"),
    ("playerDart", "Wave"),
    ("playerRobot", "Robot"),
    ("playerSpider", "Spider"),
    ("playerSwing", "Swing"),
    ("playerJetpack", "Jetpack"),
    ("playerColor", "Couleur 1"),
    ("playerColor2", "Couleur 2"),
    ("playerColor3", "Couleur glow"),
    ("playerStreak", "Trainee"),
    ("playerShipStreak", "Trainee vaisseau"),
    ("playerDeathEffect", "Effet de mort"),
]


class FieldGrid(ttk.Frame):
    """Grille de champs libelle / valeur liee a une liste de cles."""

    def __init__(self, master, fields, columns=2):
        super().__init__(master, padding=10)
        self.fields = fields
        self.vars = {}
        rows = (len(fields) + columns - 1) // columns
        for i, (key, label) in enumerate(fields):
            col, row = divmod(i, rows)
            ttk.Label(self, text=label).grid(row=row, column=col * 2, sticky="w", padx=(10, 6), pady=3)
            var = tk.StringVar()
            ttk.Entry(self, textvariable=var, width=16).grid(row=row, column=col * 2 + 1, sticky="w", pady=3)
            self.vars[key] = var

    def load(self, pdict):
        for key, var in self.vars.items():
            value = pdict.get(key, "") if pdict else ""
            var.set(value if isinstance(value, str) else "")

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
                    raise ValueError(f"{label} : '{value}' n'est pas un nombre entier")
            if value != old:
                pdict.set(key, value)


class KeyTable(ttk.Frame):
    """Tableau editable de toutes les valeurs simples d'un dictionnaire."""

    def __init__(self, master):
        super().__init__(master, padding=10)
        self.pdict = None
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 6))
        ttk.Label(bar, text="Filtre :").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(bar, textvariable=self.filter_var, width=30).pack(side="left", padx=6)
        ttk.Button(bar, text="Ajouter une cle", command=self.add_key).pack(side="right")
        ttk.Label(bar, text="Double-clic pour modifier").pack(side="right", padx=10)

        self.tree = ttk.Treeview(self, columns=("key", "type", "value"), show="headings")
        self.tree.heading("key", text="Cle")
        self.tree.heading("type", text="Type")
        self.tree.heading("value", text="Valeur")
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
            messagebox.showinfo(APP_NAME, "Valeur booleenne, rien a modifier.")
            return
        value = simpledialog.askstring(APP_NAME, f"Nouvelle valeur pour {key} :", initialvalue=elem.text or "", parent=self)
        if value is not None:
            self.pdict.set(key, value)
            self.refresh()

    def add_key(self):
        if self.pdict is None:
            return
        key = simpledialog.askstring(APP_NAME, "Nom de la cle :", parent=self)
        if not key:
            return
        value = simpledialog.askstring(APP_NAME, f"Valeur pour {key} :", parent=self)
        if value is None:
            return
        self.pdict.set(key, value)
        self.refresh()


class App(tk.Tk):
    def __init__(self, autoload=True):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("820x600")
        self.minsize(700, 450)
        self.save = None

        menu = tk.Menu(self)
        fmenu = tk.Menu(menu, tearoff=0)
        fmenu.add_command(label="Ouvrir CCGameManager.dat", command=self.open_default)
        fmenu.add_command(label="Ouvrir un fichier...", command=self.open_other)
        fmenu.add_separator()
        fmenu.add_command(label="Enregistrer", command=self.save_file, accelerator="Ctrl+S")
        fmenu.add_command(label="Enregistrer sous...", command=self.save_as)
        fmenu.add_separator()
        fmenu.add_command(label="Exporter en XML...", command=self.export_xml)
        fmenu.add_command(label="Importer un XML...", command=self.import_xml)
        fmenu.add_separator()
        fmenu.add_command(label="Restaurer la sauvegarde .bak", command=self.restore_backup)
        fmenu.add_separator()
        fmenu.add_command(label="Quitter", command=self.destroy)
        menu.add_cascade(label="Fichier", menu=fmenu)
        self.config(menu=menu)
        self.bind("<Control-s>", lambda _e: self.save_file())

        self.status = tk.StringVar(value="Aucun fichier ouvert")
        ttk.Label(self, textvariable=self.status, anchor="w", padding=(10, 4)).pack(side="bottom", fill="x")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=6, pady=6)

        stats_tab = ttk.Frame(self.tabs)
        self.stats = FieldGrid(stats_tab, STATS, columns=3)
        self.stats.pack(fill="both", expand=True)
        ttk.Button(stats_tab, text="Appliquer", command=self.apply_stats).pack(anchor="e", padx=10, pady=10)
        self.tabs.add(stats_tab, text="Statistiques")

        player_tab = ttk.Frame(self.tabs)
        self.player = FieldGrid(player_tab, PLAYER, columns=2)
        self.player.pack(fill="both", expand=True)
        ttk.Button(player_tab, text="Appliquer", command=self.apply_player).pack(anchor="e", padx=10, pady=10)
        self.tabs.add(player_tab, text="Joueur")

        self.values_table = KeyTable(self.tabs)
        self.tabs.add(self.values_table, text="Toutes les stats (GS_value)")

        self.root_table = KeyTable(self.tabs)
        self.tabs.add(self.root_table, text="Reglages et divers")

        if autoload:
            self.after(100, self.open_default)

    # Fichiers

    def load(self, path):
        try:
            self.save = gdsave.SaveFile(path)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Impossible de lire {path}\n\n{e}")
            return
        self.refresh_all()
        self.status.set(path)

    def refresh_all(self):
        data = self.save.data
        gs = data.get("GS_value")
        self.stats.load(gs)
        self.player.load(data)
        self.values_table.load(gs)
        self.root_table.load(data)

    def open_default(self):
        path = os.path.join(gdsave.default_save_dir(), "CCGameManager.dat")
        if os.path.exists(path):
            self.load(path)
        else:
            self.open_other()

    def open_other(self):
        path = filedialog.askopenfilename(
            initialdir=gdsave.default_save_dir(),
            filetypes=[("Sauvegarde GD", "*.dat"), ("Tous les fichiers", "*.*")],
        )
        if path:
            self.load(path)

    def check_open(self):
        if self.save is None:
            messagebox.showwarning(APP_NAME, "Aucun fichier ouvert.")
            return False
        return True

    def save_file(self, path=None):
        if not self.check_open():
            return
        if not messagebox.askyesno(APP_NAME, "Geometry Dash doit etre ferme, sinon il ecrasera les modifications.\n\nEnregistrer maintenant ?"):
            return
        try:
            self.save.save(path)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Erreur a l'enregistrement\n\n{e}")
            return
        target = path or self.save.path
        self.status.set(f"Enregistre : {target} (copie de l'ancien fichier en .bak)")

    def save_as(self):
        if not self.check_open():
            return
        path = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("Sauvegarde GD", "*.dat")])
        if path:
            self.save_file(path)

    def export_xml(self):
        if not self.check_open():
            return
        path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML", "*.xml")])
        if path:
            with open(path, "wb") as f:
                f.write(self.save.to_xml())
            self.status.set(f"XML exporte : {path}")

    def import_xml(self):
        if not self.check_open():
            return
        path = filedialog.askopenfilename(filetypes=[("XML", "*.xml"), ("Tous les fichiers", "*.*")])
        if not path:
            return
        try:
            with open(path, "rb") as f:
                self.save.set_xml(f.read())
        except Exception as e:
            messagebox.showerror(APP_NAME, f"XML invalide\n\n{e}")
            return
        self.refresh_all()
        self.status.set(f"XML importe depuis {path} (pas encore enregistre)")

    def restore_backup(self):
        if not self.check_open():
            return
        backup = self.save.path + ".bak"
        if not os.path.exists(backup):
            messagebox.showinfo(APP_NAME, "Aucun fichier .bak trouve.")
            return
        if messagebox.askyesno(APP_NAME, f"Remplacer le fichier actuel par\n{backup} ?"):
            with open(backup, "rb") as src, open(self.save.path, "wb") as dst:
                dst.write(src.read())
            self.load(self.save.path)

    # Edition

    def apply_stats(self):
        if not self.check_open():
            return
        try:
            self.stats.apply(self.save.data.ensure_dict("GS_value"))
        except ValueError as e:
            messagebox.showerror(APP_NAME, str(e))
            return
        self.refresh_all()
        self.status.set("Statistiques modifiees (pense a enregistrer)")

    def apply_player(self):
        if not self.check_open():
            return
        try:
            self.player.apply(self.save.data)
        except ValueError as e:
            messagebox.showerror(APP_NAME, str(e))
            return
        self.refresh_all()
        self.status.set("Joueur modifie (pense a enregistrer)")


if __name__ == "__main__":
    App().mainloop()
