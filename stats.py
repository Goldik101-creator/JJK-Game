import json
import os

from paths import data_dir

STATS_FILE = os.path.join(data_dir(), "stats.json")


def _empty():
    return {"matches": 0, "players": {}, "characters": {}}


def load():
    try:
        with open(STATS_FILE) as f:
            data = json.load(f)
        if isinstance(data, dict) and "players" in data and "characters" in data:
            return data
    except (OSError, ValueError):
        pass
    return _empty()


def save(data):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        print("(Could not save stats.)")


def reset():
    try:
        os.remove(STATS_FILE)
    except OSError:
        pass


def _record(table, key, character, result):
    entry = table.setdefault(key, {"wins": 0, "losses": 0, "draws": 0, "picks": {}})
    entry[result] += 1
    entry["picks"][character] = entry["picks"].get(character, 0) + 1


def record_match(data, seats, winner):
    """seats: two dicts like {"player": "Sam" or None, "character": "Satoru Gojo"}.
    winner: 0, 1, or None for a draw."""
    data["matches"] += 1
    for i, seat in enumerate(seats):
        if winner is None:
            result = "draws"
        else:
            result = "wins" if winner == i else "losses"
        _record(data["characters"], seat["character"], seat["character"], result)
        if seat["player"]:
            _record(data["players"], seat["player"], seat["character"], result)
    save(data)


def favorite(entry):
    picks = entry.get("picks", {})
    return max(picks, key=picks.get) if picks else "-"


def win_rate(entry):
    games = entry["wins"] + entry["losses"] + entry["draws"]
    return (entry["wins"] / games * 100) if games else 0.0
 