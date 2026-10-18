#The game's own window talks to this small local web server (standard library only).

#The window asks for the roster, starts a match, then polls for events (log lines, turn changes, "your move" prompts). The match itself runs in a background thread using the normal game engine.

import json
import mimetypes
import os
import re
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import characters
import output
import stats
from battle import MAX_TURNS, human_turn_with, run_battle
from descriptions import describe
from dialogue import draw_dialogue, intro_dialogue, victory_dialogue
from paths import data_dir, resource_path
from roster import ROSTER
from settings import DIFFICULTIES, TEXT_SPEEDS, settings
from ui import move_label, status_list
from version import __version__

MODES = {
    1: ("Human vs AI", (True, False)),
    2: ("Human vs Human", (True, True)),
    3: ("AI vs AI", (False, False)),
}

ANSI_RE = re.compile(r"\x1b\[([0-9;]*)m")
COLOR_CODES = {"90": "gray", "91": "red", "92": "green", "93": "yellow",
               "94": "blue", "95": "magenta", "96": "cyan", "97": "white"}
HP_LINE = re.compile(r".+ is at \d+ (?:hp|HP)")          # the HP bar already shows this
PASSIVE_CE_LINE = re.compile(r".+ regained \d+ CE")      # shown quietly; Focus has its own wording


STATIC_FILES = ("index.html", "style.css", "game.js")


def find_static(name):
    """Path to one of the window's files: web/<name>, or <name> beside the program if the
    web folder was not kept. Returns None if it can't be found."""
    for candidate in (resource_path("web", name), resource_path(name)):
        if os.path.isfile(candidate):
            return candidate
    return None


def missing_static_files():
    return [name for name in STATIC_FILES if find_static(name) is None]


def missing_files_message():
    folder = resource_path("web")
    return ("The game's window files were not found: " + ", ".join(missing_static_files()) + ".\n"
            f"They belong in a folder named 'web' next to play.py, i.e. here:\n{folder}\n"
            "Copy the whole 'web' folder from the zip (it contains index.html, style.css and game.js).")


def to_segments(text):
    """Turn text containing ANSI colors into [{"t": text, "c": color, "b": bold}, ...]."""
    segments, color, bold, pos = [], None, False, 0
    for match in ANSI_RE.finditer(text):
        if match.start() > pos:
            segments.append({"t": text[pos:match.start()], "c": color, "b": bold})
        for code in (match.group(1) or "0").split(";"):
            if code in ("", "0"):
                color, bold = None, False
            elif code == "1":
                bold = True
            elif code in COLOR_CODES:
                color = COLOR_CODES[code]
        pos = match.end()
    if pos < len(text):
        segments.append({"t": text[pos:], "c": color, "b": bold})
    return segments


def trim_newlines(segments):
    """Remove blank lines at the start and end of the text (the engine uses them for spacing)."""
    for seg in segments:
        seg["t"] = seg["t"].lstrip("\n")
        if seg["t"]:
            break
    for seg in reversed(segments):
        seg["t"] = seg["t"].rstrip("\n")
        if seg["t"]:
            break
    return [seg for seg in segments if seg["t"]]


def move_info(fighter, move):
    return {"name": move.name, "label": move_label(move), "ce": move.ce_cost,
            "cd": move.cooldown, "desc": describe(move, fighter)}


def fighter_card(index, cls):
    f = cls()
    return {"index": index, "name": f.name, "title": f.title, "hp": f.max_hp, "ce": f.max_ce,
            "tip": f.tip, "moves": [move_info(f, m) for m in f.moves]}


def fighter_state(f):
    return {"name": f.name, "hp": f.hp, "max_hp": f.max_hp, "ce": f.ce, "max_ce": f.max_ce,
            "tags": [{"text": text, "color": color} for text, color in status_list(f)]}


def log_crash(message):
    try:
        with open(os.path.join(data_dir(), "crash.log"), "a", encoding="utf-8") as file:
            file.write(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} (version {__version__}) ---\n{message}\n")
    except OSError:
        pass


class Aborted(Exception):
    """Raised inside the match thread when the player leaves the match."""


class Session:
    def __init__(self, mode, names, picks):
        self.mode = mode
        self.humans = MODES[mode][1]
        self.names = [names[0] if self.humans[0] else None, names[1] if self.humans[1] else None]
        self.picks = picks
        self.p1, self.p2 = ROSTER[picks[0]](), ROSTER[picks[1]]()
        self.p1.ai, self.p2.ai = not self.humans[0], not self.humans[1]
        self.events = []
        self.cond = threading.Condition()
        self.pending = None
        self.answer = None
        self.aborted = False
        self.done = False
        self.phase = "battle"
        self.thread = None

    def emit(self, event):
        with self.cond:
            self.events.append(event)
            self.cond.notify_all()

    def label(self, who):
        if self.names[who]:
            return self.names[who]
        return "AI" if self.mode == 1 else f"AI {who + 1}"

    def snapshot(self):
        return [fighter_state(self.p1), fighter_state(self.p2)]

    def sink(self, text):
        """Every line of game text arrives here instead of the terminal."""
        plain = ANSI_RE.sub("", text)
        stripped = plain.strip()
        if not stripped or HP_LINE.fullmatch(stripped):
            return
        tone = "quiet" if PASSIVE_CE_LINE.fullmatch(stripped) else self.phase
        self.emit({"t": "log", "segs": trim_newlines(to_segments(text)), "gap": plain.startswith("\n"),
                   "tone": tone, "state": self.snapshot()})

    def _wait(self, kind):
        with self.cond:
            self.pending, self.answer = kind, None
            while self.answer is None:
                if self.aborted:
                    raise Aborted()
                self.cond.wait(timeout=0.5)
            value, self.pending = self.answer, None
            return value

    def give(self, kind, value):
        with self.cond:
            if self.pending != kind:
                return False
            self.answer = value
            self.cond.notify_all()
            return True

    def pick_move(self, f, _enemy):
        who = 0 if f is self.p1 else 1
        moves = []
        for i, move in enumerate(f.moves):
            cooldown = f.cooldown[move.name]
            if cooldown > 0:
                why = "cooldown"
            elif f.ce < move.ce_cost and move.name != "Focus":
                why = "ce"
            else:
                why = ""
            moves.append({"i": i, "name": move.name, "label": move_label(move), "ce": move.ce_cost,
                          "cd": cooldown, "ok": not why, "why": why, "desc": describe(move, f)})
        self.emit({"t": "prompt", "kind": "move", "who": who, "label": self.label(who),
                   "moves": moves, "state": self.snapshot()})
        return self._wait("move")

    def pick_rika(self, f, options):
        who = 0 if f is self.p1 else 1
        self.emit({"t": "prompt", "kind": "rika", "who": who, "label": self.label(who),
                   "options": [{"i": i, "name": m.name, "label": move_label(m)} for i, m in enumerate(options)]})
        return options[self._wait("rika")]

    def on_turn(self, number):
        self.emit({"t": "turn", "n": number, "max": MAX_TURNS})

    def on_actor(self, attacker, _p1, _p2):
        self.emit({"t": "actor", "who": 0 if attacker is self.p1 else 1, "state": self.snapshot()})

    def run(self):
        try:
            output.set_sink(self.sink)
            characters.RIKA_CHOOSER = self.pick_rika
            self.emit({"t": "start", "mode": self.mode,
                       "fighters": [fighter_card(self.picks[0], ROSTER[self.picks[0]]),
                                    fighter_card(self.picks[1], ROSTER[self.picks[1]])],
                       "labels": [self.label(0), self.label(1)], "humans": list(self.humans),
                       "state": self.snapshot()})
            self.phase = "intro"
            intro_dialogue(self.p1, self.p2)
            self.phase = "battle"
            winner, turns = run_battle(self.p1, self.p2, human=human_turn_with(self.pick_move),
                                       on_turn=self.on_turn, on_actor=self.on_actor)
            if winner is None:
                draw_dialogue(self.p1, self.p2)
            else:
                victory_dialogue((self.p1, self.p2)[winner], (self.p1, self.p2)[1 - winner])
            if any(self.humans):
                stats.record_match(stats.load(), [
                    {"player": self.names[0], "character": self.p1.name},
                    {"player": self.names[1], "character": self.p2.name},
                ], winner)
            self.emit({"t": "end", "winner": winner, "turns": turns, "labels": [self.label(0), self.label(1)],
                       "names": [self.p1.name, self.p2.name], "state": self.snapshot()})
        except Aborted:
            pass
        except Exception:                      # noqa: BLE001 - tell the window, keep a log for the developer
            message = traceback.format_exc()
            log_crash(message)
            self.emit({"t": "error", "message": message.strip().splitlines()[-1]})
        finally:
            output.set_sink(None)
            characters.RIKA_CHOOSER = None
            with self.cond:
                self.done = True
                self.cond.notify_all()

    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def abort(self):
        with self.cond:
            self.aborted = True
            self.cond.notify_all()
        if self.thread is not None:
            self.thread.join(timeout=3)


class GameServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0):
        super().__init__(("127.0.0.1", port), Handler)
        self.port = self.server_address[1]
        self.session = None
        self.session_id = 0
        self.lock = threading.Lock()
        self.last_ping = time.time()
        self.closing_at = None
        self.closing_page = None
        self.quit_requested = False
        self.roster_cards = [fighter_card(i, cls) for i, cls in enumerate(ROSTER)]

    def new_session(self, mode, names, picks):
        with self.lock:
            if self.session is not None:
                self.session.abort()
            self.session_id += 1
            self.session = Session(mode, names, picks)
            self.session.start()
            return self.session_id

    def should_stop(self):
        """True when the player closed the window, pressed Quit, or has been gone a long time."""
        now = time.time()
        if self.quit_requested:
            return True
        if self.closing_at is not None and now - self.closing_at > 3:
            return True
        return now - self.last_ping > 300


class Handler(BaseHTTPRequestHandler):
    server_version = "JJKClash"

    def log_message(self, *args):        # keep the console quiet
        pass

    def _send(self, status, body, content_type="application/json", cache="no-store"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        try:
            data = json.loads(self.rfile.read(min(length, 100_000)).decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except ValueError:
            return {}

    def _static(self, name):
        path = find_static(name) if name in STATIC_FILES else None
        if path is None:
            page = ("<!doctype html><meta charset='utf-8'><body style='font-family:sans-serif;background:#0a0a14;"
                    "color:#e8e8f2;padding:40px;line-height:1.6'><h2>Clash of Sorcerers can't find its window files</h2>"
                    f"<pre style='white-space:pre-wrap;font-size:15px'>{missing_files_message()}</pre></body>")
            return self._send(404, page.encode("utf-8"), "text/html; charset=utf-8")
        with open(path, "rb") as file:
            content = file.read()
        kind = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if kind.startswith("text/") or kind.endswith("javascript"):
            kind += "; charset=utf-8"
        self._send(200, content, kind, cache="no-cache")

    # -- routes ------------------------------------------------------------
    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {"error": "forbidden"})
        url = urlparse(self.path)
        query = parse_qs(url.query)
        try:
            if url.path in ("/", "/index.html"):
                return self._static("index.html")
            if url.path in ("/style.css", "/game.js"):
                return self._static(url.path.lstrip("/"))
            if url.path == "/api/bootstrap":
                return self._send(200, self.api_bootstrap())
            if url.path == "/api/poll":
                return self._send(200, self.api_poll(query))
            if url.path == "/api/stats":
                return self._send(200, self.api_stats())
            return self._send(404, {"error": "not found"})
        except Exception:                      # noqa: BLE001
            log_crash(traceback.format_exc())
            return self._send(500, {"error": "server error"})

    def do_POST(self):

        if not self._host_ok() or self.headers.get("X-Game") != "1":
            return self._send(403, {"error": "forbidden"})
        url = urlparse(self.path)
        body = self._body()
        try:
            routes = {
                "/api/start": self.api_start, "/api/move": self.api_move, "/api/rika": self.api_rika,
                "/api/abort": self.api_abort, "/api/settings": self.api_settings,
                "/api/stats/reset": self.api_stats_reset, "/api/ping": self.api_ping,
                "/api/closing": self.api_closing, "/api/shutdown": self.api_shutdown,
            }
            if url.path not in routes:
                return self._send(404, {"error": "not found"})
            return self._send(200, routes[url.path](body))
        except Exception:                      # noqa: BLE001
            log_crash(traceback.format_exc())
            return self._send(500, {"error": "server error"})


    def api_bootstrap(self):
        return {"version": __version__, "max_turns": MAX_TURNS, "roster": self.server.roster_cards,
                "modes": [{"id": k, "label": v[0], "humans": list(v[1])} for k, v in MODES.items()],
                "settings": self.settings_payload()}

    @staticmethod
    def settings_payload():
        return {"text_speed": settings.text_speed, "ai_difficulty": settings.ai_difficulty,
                "show_descriptions": settings.show_descriptions, "show_dialogue": settings.show_dialogue,
                "speeds": list(TEXT_SPEEDS), "difficulties": list(DIFFICULTIES)}

    def api_poll(self, query):
        session = self.server.session
        sid = int(query.get("sid", ["0"])[0])
        since = int(query.get("since", ["0"])[0])
        if session is None or sid != self.server.session_id:
            return {"stale": True, "events": [], "next": since, "done": True}
        with session.cond:
            session.cond.wait_for(lambda: len(session.events) > since or session.done or session.aborted,
                                  timeout=10)
            return {"stale": False, "events": session.events[since:], "next": len(session.events),
                    "done": session.done}

    def api_stats(self):
        data = stats.load()

        def rows(table):
            out_rows = [{"name": name, "wins": e["wins"], "losses": e["losses"], "draws": e["draws"],
                         "rate": round(stats.win_rate(e), 1), "favorite": stats.favorite(e)}
                        for name, e in table.items()]
            return sorted(out_rows, key=lambda r: (-r["rate"], r["name"]))
        return {"matches": data["matches"], "players": rows(data["players"]), "fighters": rows(data["characters"])}

    def api_start(self, body):
        mode = body.get("mode")
        picks = body.get("picks")
        names = body.get("names") or ["Player 1", "Player 2"]
        if mode not in MODES or not isinstance(picks, list) or len(picks) != 2:
            return {"ok": False, "error": "bad request"}
        if not all(isinstance(p, int) and 0 <= p < len(ROSTER) for p in picks):
            return {"ok": False, "error": "bad fighter"}
        clean = [(str(n).strip()[:16] or f"Player {i + 1}") for i, n in enumerate((list(names) + ["", ""])[:2])]
        if MODES[mode][1] == (True, True) and clean[0].lower() == clean[1].lower():
            clean[1] = clean[1][:12] + " (2)"
        return {"ok": True, "sid": self.server.new_session(mode, clean, picks)}

    def _session_give(self, kind, value):
        session = self.server.session
        return {"ok": bool(session and session.give(kind, value))}

    def api_move(self, body):
        index = body.get("index")
        return self._session_give("move", index) if isinstance(index, int) else {"ok": False}

    def api_rika(self, body):
        index = body.get("index")
        return self._session_give("rika", index) if isinstance(index, int) and 0 <= index < 5 else {"ok": False}

    def api_abort(self, _body):
        session = self.server.session
        if session is not None:
            session.abort()
        return {"ok": True}

    def api_settings(self, body):
        if body.get("text_speed") in TEXT_SPEEDS:
            settings.text_speed = body["text_speed"]
        if body.get("ai_difficulty") in DIFFICULTIES:
            settings.ai_difficulty = body["ai_difficulty"]
        for key in ("show_descriptions", "show_dialogue"):
            if isinstance(body.get(key), bool):
                setattr(settings, key, body[key])
        settings.save()
        return {"ok": True, "settings": self.settings_payload()}

    def api_stats_reset(self, _body):
        stats.reset()
        return {"ok": True}

    def api_ping(self, body):
        page = body.get("page")
        if page is not None and page == self.server.closing_page:
            return {"ok": True}            # a late ping from a page that is already closing
        self.server.last_ping = time.time()
        if self.server.closing_page is not None:   # a different page opened (e.g. a reload): keep running
            self.server.closing_page = None
            self.server.closing_at = None
        return {"ok": True}

    def api_closing(self, body):
        self.server.closing_at = time.time()
        self.server.closing_page = body.get("page")
        return {"ok": True}

    def api_shutdown(self, _body):
        self.server.quit_requested = True
        return {"ok": True}
