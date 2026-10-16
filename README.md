# GDSpartiat

Editeur de sauvegarde pour Geometry Dash (version PC Windows).

Il decode `CCGameManager.dat`, affiche les valeurs et permet de les modifier puis de re-encoder le fichier.

## Utilisation

1. Telecharger `GDSpartiat.exe` dans la page [Releases](https://github.com/LCournollet/GDSpartiat/releases).
2. Fermer Geometry Dash (sinon le jeu ecrase le fichier en quittant).
3. Lancer l'exe. Le fichier `%LOCALAPPDATA%\GeometryDash\CCGameManager.dat` est ouvert automatiquement.
4. Modifier les valeurs puis cliquer sur "Appliquer" et faire `Ctrl+S`.

A chaque enregistrement, l'ancien fichier est copie en `CCGameManager.dat.bak`. Il peut etre remis en place via `Fichier > Restaurer la sauvegarde .bak`.

## Onglets

- **Statistiques** : etoiles, lunes, diamants, orbes, cles demon, coins, shards, etc.
- **Joueur** : pseudo, icones, couleurs.
- **Toutes les stats (GS_value)** : toutes les cles de stats, y compris celles non listees.
- **Reglages et divers** : les autres valeurs simples du fichier.

Le menu Fichier permet aussi d'exporter la sauvegarde decodee en XML et de reimporter un XML modifie a la main.

## Remarques

- Modifier ses stats puis synchroniser son compte peut entrainer un ban du classement.
- Les fichiers de la version Mac (chiffres en AES) ne sont pas pris en charge.

## Lancer depuis les sources

```
python app.py
```

Construire l'exe :

```
pip install pyinstaller
pyinstaller --onefile --windowed --name GDSpartiat app.py
```
