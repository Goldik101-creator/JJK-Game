# Jujutsu Kaisen: Clash of Sorcerers

A turn-based battle game with 21 fighters, built in Python. Pick a fighter, manage your cursed energy (CE),
time your cooldowns, and open your domain at the right moment.

> Fan project. Not affiliated with or endorsed by Gege Akutami, Shueisha, or MAPPA. Free, non-commercial,
> and contains no official art or audio.

![Battle screen](screenshots/battle.png)

## Run it

Needs Python 3.9 or newer and Microsoft Edge or Google Chrome. There is nothing to install.

```
python play.py
```

The game opens in its own window. It runs a small server on your own computer (nothing goes over the
internet) and shows it in an app-style Edge or Chrome window. Closing the window closes the game. If neither
browser is found, your default browser is used instead.

Prefer the terminal? `python main1.py` plays the original text version.

## If the window shows an error

- **"can't find its window files"** (or `{"error": "not found"}`): the `web` folder must sit next to `play.py`
  and contain `index.html`, `style.css` and `game.js`. Copy the whole folder from the zip.
- **`No module named ...`**: every `.py` file from the zip must be in the same folder as `play.py`.

## Game modes

- **Human vs AI**: fight the computer (difficulty is set in Settings)
- **Human vs Human**: two players on one keyboard
- **AI vs AI**: watch two fighters battle

## How a fight works

The game has a built-in **How to Play** screen. In short:

- Each turn you pick one move. Moves cost CE and have cooldowns. **Focus** skips your attack to regain CE.
- Dodges, crits, burn and freeze are random. Domains boost your attacks for 4 turns. Simple Domain shields
  you against the next 2 enemy turns.
- Fighters have their own mechanics: Choso's Blood Stacks, Naoya's Speed stacks, Mei Mei's crows,
  Kashimo's Charge, Inumaki's Strain, and more.
- Keys: **1-8** choose a move, **Space** skips the text, **Esc** opens the menu.

## Where your data is saved

Settings, stats and any crash log (`settings.json`, `stats.json`, `crash.log`) are saved next to the game files
when you run from source, and in `%APPDATA%\JJKClash` when you run the packaged Windows version.

## Making a version for friends (Windows)

On a Windows computer with Python installed, run `build.bat`. It creates `dist\ClashOfSorcerers`. Zip that
folder and share it. Players do not need Python. Windows may show a SmartScreen warning because the program is
not code-signed; choose "More info" then "Run anyway". On Mac or Linux, run `sh build.sh` on that system.

## Project layout

| File | What it does |
|---|---|
| `play.py` | opens the game window |
| `server.py` | the small local server that runs matches for the window |
| `web/` | the window itself: `index.html`, `style.css`, `game.js` |
| `main1.py` | the original terminal version |
| `characters.py` | the `Jjk` base class (damage, dodging, AI) and every fighter |
| `battle.py` | the turn loop |
| `output.py` | sends the game's text to the terminal or to the window |
| `ui.py` | terminal colors, bars and cards |
| `descriptions.py` | the text for every move |
| `dialogue.py` | pre-battle scenes |
| `roster.py` | the list of selectable fighters |
| `settings.py`, `stats.py`, `paths.py` | saved settings, match records, file locations |
| `test_game.py` | tests |

## Adding a fighter

1. In `characters.py`, subclass `Jjk`, call `super().__init__(name, hp, ce, tip, title)` and add moves with
   `self.add_moves(Move(name, damage, cooldown, ce_cost), start_cd=...)`.
2. Add the class to `ROSTER` in `roster.py` (or to `NEW_ROSTER` at the bottom of `characters.py`).
3. Add a line for each new move to `descriptions.py`.
4. For a unique mechanic, override one of the hooks: `on_turn_tick`, `on_hit`, `modify_outgoing`,
   `modify_incoming`. To show it in the status panel, add it to the class's `STATUS` dictionary.
5. Optionally pick a color for the fighter in `FIGHTER_COLORS` at the top of `web/game.js`.
6. Run `python test_game.py`. It fails if a move has no description or a fighter can't finish a match.

## Tests

```
python test_game.py
```
