#Tests for the game. Run with: test_game.py 

import contextlib
import io
import json
import os
import random
import re
import tempfile
import threading
import time
import urllib.error
import urllib.request

os.environ.setdefault("JJK_DATA_DIR", tempfile.mkdtemp())   # tests never touch your real settings or stats

import characters
import settings as settings_module
from battle import MAX_TURNS, run_battle
from characters import Jjk, Megumi, Sukuna, Kashimo, MeiMei, Inumaki, Gojo
from descriptions import DESCRIPTIONS, OVERRIDES, describe
from roster import ROSTER
from settings import Settings, settings
from ui import status_tags
import server as game_server
import stats


@contextlib.contextmanager
def quiet_and_fast():
    old = (settings.text_speed, settings.colors, settings.ai_difficulty)
    settings.text_speed, settings.colors = "instant", False
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            yield
    finally:
        settings.text_speed, settings.colors, settings.ai_difficulty = old


@contextlib.contextmanager
def no_dodging():
    old = Jjk._dodge_message
    Jjk._dodge_message = lambda self, enemy, move: None
    try:
        yield
    finally:
        Jjk._dodge_message = old


# ---------------------------------------------------------------- descriptions
def test_every_move_has_a_description():
    missing = []
    for cls in ROSTER:
        fighter = cls()
        for move in fighter.moves:
            if move.name not in DESCRIPTIONS and (fighter.name, move.name) not in OVERRIDES:
                missing.append(f"{fighter.name}: {move.name}")
    assert not missing, f"moves without a description: {missing}"


def test_no_leftover_descriptions():
    used = {m.name for cls in ROSTER for m in cls().moves}
    leftover = sorted(set(DESCRIPTIONS) - used)
    assert not leftover, f"descriptions for moves that no fighter has: {leftover}"


def test_descriptions_render_cleanly():
    for cls in ROSTER:
        fighter = cls()
        for move in fighter.moves:
            text = describe(move, fighter)
            assert text and "{" not in text and "}" not in text, f"{move.name}: {text!r}"


# ---------------------------------------------------------------- settings
def test_settings_are_saved_and_loaded():
    old_file = settings_module.SETTINGS_FILE
    with tempfile.TemporaryDirectory() as folder:
        settings_module.SETTINGS_FILE = os.path.join(folder, "settings.json")
        try:
            a = Settings()
            a.show_dialogue = False
            a.text_speed = "fast"
            a.ai_difficulty = "hard"
            a.colors = False
            a.show_descriptions = False
            a.save()
            b = Settings()
            b.load()
            assert (b.show_dialogue, b.text_speed, b.ai_difficulty, b.colors, b.show_descriptions) == \
                   (False, "fast", "hard", False, False)
        finally:
            settings_module.SETTINGS_FILE = old_file


def test_text_speed_controls_battle_pauses():
    """Every pause in the game (including characters.py) must go through the setting."""
    import ui
    slept = []
    real_sleep = ui.time.sleep
    ui.time.sleep = lambda s: slept.append(s)
    old = settings.text_speed
    try:
        settings.text_speed = "instant"
        with contextlib.redirect_stdout(io.StringIO()):
            Gojo().attack(Sukuna(), 0)
        assert not slept, "instant text speed should not sleep at all"
        settings.text_speed = "slow"
        with contextlib.redirect_stdout(io.StringIO()):
            Gojo().attack(Sukuna(), 0)
        assert slept and set(slept) == {1.2}, slept
    finally:
        settings.text_speed = old
        ui.time.sleep = real_sleep


# ---------------------------------------------------------------- whole matches
def test_every_fighter_can_finish_matches():
    random.seed(1)
    with quiet_and_fast():
        for cls in ROSTER:
            for _ in range(6):
                a, b = cls(), random.choice(ROSTER)()
                a.ai = b.ai = True
                winner, turns = run_battle(a, b)
                assert winner in (0, 1, None) and 1 <= turns <= MAX_TURNS


# ---------------------------------------------------------------- AI
def _ready(fighter):
    for name in fighter.cooldown:
        fighter.cooldown[name] = 0
    fighter.ce = fighter.max_ce


def test_ai_saves_stalemate_moves_for_when_it_is_losing():
    mahoraga = next(i for i, m in enumerate(Megumi().moves) if m.name == "Divine General MAHORAGA")
    with quiet_and_fast():
        random.seed(3)
        winning = Megumi(); _ready(winning); enemy = Sukuna(); enemy.hp = 40
        assert all(winning.choose_move(enemy) != mahoraga for _ in range(300))
        losing = Megumi(); _ready(losing); losing.hp = 30
        assert any(losing.choose_move(Sukuna()) == mahoraga for _ in range(300))


def test_ai_difficulty_changes_how_it_plays():
    def strongest_rate(level):
        settings.ai_difficulty = level
        random.seed(5)
        fighter, enemy = Sukuna(), Gojo()
        _ready(fighter)
        best = max(range(len(fighter.moves)), key=lambda i: fighter._ai_value(fighter.moves[i], enemy))
        return sum(fighter.choose_move(enemy) == best for _ in range(600)) / 600
    with quiet_and_fast():
        easy, normal, hard = strongest_rate("easy"), strongest_rate("normal"), strongest_rate("hard")
    assert easy < normal < hard, (easy, normal, hard)


# ---------------------------------------------------------------- new fighters' mechanics
def test_mei_mei_crows_peck_the_enemy():
    with quiet_and_fast(), no_dodging():
        mei, enemy = MeiMei(), Gojo()
        mei.attack(enemy, 2)                     # Summon Crows
        assert mei.crows == 2
        before = enemy.hp
        mei.apply_status_effect(enemy)           # start of her turn
        assert before - enemy.hp == 10


def test_kashimo_gains_charge_and_amber_spends_it():
    with quiet_and_fast(), no_dodging():
        kashimo, enemy = Kashimo(), Gojo()
        for _ in range(4):
            kashimo.apply_status_effect(enemy)
        assert kashimo.charge == 4
        kashimo.cooldown["Mythical Beast Amber"] = 0
        kashimo.attack(enemy, 3)
        assert kashimo.charge == 0


def test_inumaki_throat_gives_out_after_four_commands():
    with quiet_and_fast(), no_dodging():
        inumaki, enemy = Inumaki(), Sukuna()
        for _ in range(4):
            inumaki.cooldown["Crush"] = 0
            inumaki.ce = inumaki.max_ce
            inumaki.attack(enemy, 1)
        assert inumaki.strain == 0               # backlash reset it


def test_status_panel_shows_the_new_mechanics():
    with quiet_and_fast():
        mei, kashimo, inumaki, victim = MeiMei(), Kashimo(), Inumaki(), Gojo()
        mei.crows, kashimo.charge, inumaki.strain, victim.chill = 3, 5, 3, 2
        assert any("Crows x3" in t for t in status_tags(mei))
        assert any("Charge x5" in t for t in status_tags(kashimo))
        assert any("Strain x3" in t for t in status_tags(inumaki))
        assert any("Chill x2" in t for t in status_tags(victim))


# ---------------------------------------------------------------- the window's server
@contextlib.contextmanager
def serving():
    """A real game server on a free port, for the duration of a test."""
    srv = game_server.GameServer(0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield srv, f"http://127.0.0.1:{srv.port}"
    finally:
        if srv.session is not None:
            srv.session.abort()
        srv.shutdown()
        srv.server_close()


def _get(base, path):
    return json.load(urllib.request.urlopen(base + path))


def _post(base, path, body=None):
    request = urllib.request.Request(base + path, data=json.dumps(body or {}).encode(),
                                     headers={"X-Game": "1", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(request))


def _play_through(base, sid, answer=None, limit=40):
    """Poll a match until it finishes. answer(prompt) -> (path, body) answers move prompts."""
    events, since, started = [], 0, time.time()
    while True:
        reply = _get(base, f"/api/poll?sid={sid}&since={since}")
        for event in reply["events"]:
            events.append(event)
            if event["t"] == "prompt" and answer is not None:
                path, body = answer(event)
                assert _post(base, path, body)["ok"]
        since = reply["next"]
        if reply["done"]:
            return events
        assert time.time() - started < limit, "match did not finish in time"


def test_colors_in_game_text_become_segments():
    segments = game_server.to_segments("plain \x1b[91mred\x1b[0m \x1b[1m\x1b[93mbold yellow\x1b[0m")
    assert [(s["t"], s["c"], s["b"]) for s in segments] == [
        ("plain ", None, False), ("red", "red", False), (" ", None, False), ("bold yellow", "yellow", True)]


def test_window_files_are_present():
    from paths import resource_path
    for name in ("index.html", "style.css", "game.js"):
        assert os.path.isfile(resource_path("web", name)), name


def test_missing_window_files_are_explained_and_loose_files_still_work():
    real = game_server.resource_path
    try:
        with tempfile.TemporaryDirectory() as empty:
            game_server.resource_path = lambda *parts: os.path.join(empty, *parts)
            assert game_server.missing_static_files() == list(game_server.STATIC_FILES)
            with serving() as (srv, base):
                try:
                    urllib.request.urlopen(base + "/")
                    raise AssertionError("expected a 404")
                except urllib.error.HTTPError as error:
                    page = error.read().decode()
                    assert error.code == 404 and "web" in page and "play.py" in page   # a helpful page, not bare JSON
            for name in game_server.STATIC_FILES:             # the same files saved loose, with no web folder
                with open(os.path.join(empty, name), "w") as file:
                    file.write("<html>ok</html>")
            assert game_server.missing_static_files() == []
            with serving() as (srv, base):
                assert urllib.request.urlopen(base + "/").status == 200
    finally:
        game_server.resource_path = real


def test_server_ai_match_streams_to_the_end():
    with quiet_and_fast(), serving() as (srv, base):
        boot = _get(base, "/api/bootstrap")
        assert len(boot["roster"]) == len(ROSTER) and boot["max_turns"] == MAX_TURNS
        sid = _post(base, "/api/start", {"mode": 3, "picks": [1, 9], "names": ["a", "b"]})["sid"]
        events = _play_through(base, sid)
        kinds = [e["t"] for e in events]
        assert kinds[0] == "start" and kinds[-1] == "end" and "log" in kinds and "turn" in kinds
        lines = ["".join(seg["t"] for seg in e["segs"]) for e in events if e["t"] == "log"]
        assert lines and not any(re.fullmatch(r".+ is at \d+ (?:hp|HP)", line) for line in lines)   # the bars show HP


def test_server_human_match_can_be_played_including_call_to_rika():
    random.seed(3)

    def answer(event):
        if event["kind"] == "rika":
            return "/api/rika", {"index": random.randrange(5)}
        usable = [m["i"] for m in event["moves"] if m["ok"]]
        wants_rika = 4 in usable and event["who"] == 0
        return "/api/move", {"index": 4 if wants_rika else random.choice(usable)}

    with quiet_and_fast(), serving() as (srv, base):
        before = stats.load()["matches"]
        sid = _post(base, "/api/start", {"mode": 1, "picks": [7, 4], "names": ["Sam", ""]})["sid"]   # Yuta vs Megumi
        events = _play_through(base, sid, answer)
        assert events[-1]["t"] == "end" and events[-1]["labels"] == ["Sam", "AI"]
        assert any(e["t"] == "prompt" and e["kind"] == "rika" for e in events)
        assert stats.load()["matches"] == before + 1             # human matches are recorded


def test_server_can_abort_a_match():
    with quiet_and_fast(), serving() as (srv, base):
        sid = _post(base, "/api/start", {"mode": 2, "picks": [0, 1], "names": ["A", "B"]})["sid"]
        time.sleep(0.3)
        assert _post(base, "/api/abort")["ok"]
        assert _get(base, f"/api/poll?sid={sid}&since=0")["done"]


def test_server_ignores_requests_that_do_not_come_from_the_game_window():
    with serving() as (srv, base):
        def status(request):
            try:
                urllib.request.urlopen(request)
                return 200
            except urllib.error.HTTPError as error:
                return error.code
        assert status(urllib.request.Request(base + "/api/abort", data=b"{}", method="POST")) == 403      # no X-Game header
        assert status(urllib.request.Request(base + "/api/bootstrap", headers={"Host": "evil.example.com"})) == 403
        assert status(base + "/..%2f..%2fetc%2fpasswd") == 404


def test_closing_the_window_stops_the_server_but_a_reload_does_not():
    with serving() as (srv, base):
        _post(base, "/api/ping", {"page": "one"})
        _post(base, "/api/closing", {"page": "one"})                 # window one is closing...
        _post(base, "/api/ping", {"page": "two"})                    # ...and a new page opened (a reload)
        assert srv.closing_page is None and not srv.should_stop()
        _post(base, "/api/closing", {"page": "two"})
        _post(base, "/api/ping", {"page": "two"})                    # late ping from the closing page is ignored
        srv.closing_at -= 4
        assert srv.should_stop()


# ---------------------------------------------------------------- tiny runner (no pytest needed)
if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as error:               # noqa: BLE001 - show every failure, then exit non-zero
            failed += 1
            print(f"FAIL  {name}: {type(error).__name__}: {error}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)
