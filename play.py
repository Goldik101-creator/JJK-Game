#Start the game in its own window.   Run:  python play.py

#How it works: the game runs a small server on your own computer and opens it in an app-style, window of Microsoft Edge or Google Chrome (no address bar, no tabs). Nothing is sent over the internet.If neither is found, your default browser is used instead.

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import threading
import time
import traceback
import webbrowser

from paths import data_dir
from server import GameServer, log_crash, missing_files_message, missing_static_files
from version import __version__

WINDOW_SIZE = "1200,780"


def find_browser():
    custom = os.environ.get("JJK_BROWSER")
    if custom and os.path.exists(custom):
        return custom
    if sys.platform.startswith("win"):
        roots = [os.environ.get(v) for v in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA")]
        relatives = [r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe",
                     r"BraveSoftware\Brave-Browser\Application\brave.exe"]
        for relative in relatives:
            for root in filter(None, roots):
                path = os.path.join(root, relative)
                if os.path.exists(path):
                    return path
    elif sys.platform == "darwin":
        for path in ("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                     "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                     "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"):
            if os.path.exists(path):
                return path
    else:
        for name in ("microsoft-edge", "google-chrome", "google-chrome-stable", "chromium",
                     "chromium-browser", "brave-browser"):
            path = shutil.which(name)
            if path:
                return path
    return None


def open_window(url):
    
    exe = find_browser()
    if exe:
        # A private profile folder keeps the game window separate from your normal browser,
        # so closing the game window ends this browser process (and therefore the game).
        profile = os.path.join(data_dir(), "browser-profile")
        args = [exe, f"--app={url}", f"--user-data-dir={profile}", "--no-first-run",
                "--no-default-browser-check", f"--window-size={WINDOW_SIZE}"]
        args += shlex.split(os.environ.get("JJK_BROWSER_ARGS", ""))
        try:
            return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass
    webbrowser.open(url)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Clash of Sorcerers")
    parser.add_argument("--no-window", action="store_true", help="only start the server and print its address")
    parser.add_argument("--port", type=int, default=0, help="port to use (default: any free port)")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    if missing_static_files():
        message = missing_files_message()
        print(message)
        log_crash(message)
        return 1

    server = GameServer(args.port)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.port}/"
    print(f"Clash of Sorcerers {__version__} is running at {url}")
    started = time.time()
    process = None if args.no_window else open_window(url)
    if args.no_window:
        print("Press Ctrl+C to stop.")

    try:
        while not server.should_stop():
            # The browser process ending means the window was closed. Ignore a process that exits
            # right away: it handed the window to an already-running browser.
            if process is not None and process.poll() is not None and time.time() - started > 6:
                break
            time.sleep(0.4)
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:                      # noqa: BLE001 - keep a log, because the .exe has no console
        log_crash(traceback.format_exc())
        raise
