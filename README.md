# GDSpartiat

Save editor for Geometry Dash (Windows PC version).

It decodes `CCGameManager.dat`, shows its values, lets you edit them and encodes the file back.

## Usage

1. Download `GDSpartiat.exe` from the [Releases](https://github.com/LCournollet/GDSpartiat/releases) page.
2. Close Geometry Dash (otherwise the game overwrites the file when it exits).
3. Run the exe. `%LOCALAPPDATA%\GeometryDash\CCGameManager.dat` is opened automatically.
4. Edit the values, then click "Save" (or press `Ctrl+S`).

The app refuses to save while Geometry Dash is running, and warns you if you quit with unsaved changes.

Every time you save, the previous file is copied to `CCGameManager.dat.bak`. You can put it back with `File > Restore .bak backup`.

## Tabs

- **Stats**: stars, moons, diamonds, orbs, demon keys, coins, shards, etc. "Orbs (shop)" are the orbs you can spend, "Orbs (total)" is the counter shown in the in-game stats.
- **Player**: username, icons, colors.
- **All stats (GS_value)**: every stat key, including the ones not listed above.
- **Settings and misc**: the other simple values in the file.

The File menu can also export the decoded save to XML and import an XML file edited by hand.

## Notes

- Editing your stats and then syncing your account can get you banned from the leaderboards.
- Mac save files (AES encrypted) are not supported.

## Running from source

```
python app.py
```

Building the exe:

```
pip install pyinstaller
pyinstaller --onefile --windowed --name GDSpartiat app.py
```
