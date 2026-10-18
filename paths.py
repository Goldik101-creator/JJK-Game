#Where the game finds its files and where it saves things.

#When packaged as a single .exe, the program runs from a temporary folder that is deleted on exit,
#so settings and stats are saved in a permanent per-user folder instead.
#Set the JJK_DATA_DIR environment variable to use a different folder (handy for testing).
import os
import sys


def resource_path(*parts):
    """Read-only files that ship with the game, such as the web/ folder."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def data_dir():
    """A folder the game can write to: settings.json, stats.json and crash.log."""
    custom = os.environ.get("JJK_DATA_DIR")
    if custom:
        path = custom
    elif getattr(sys, "frozen", False):
        root = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".local", "share")
        path = os.path.join(root, "JJKClash")
    else:
        path = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(path, exist_ok=True)
    return path
