import json
import os

from paths import data_dir

SETTINGS_FILE = os.path.join(data_dir(), "settings.json")

# seconds of pause between battle-log lines
TEXT_SPEEDS = {"instant": 0.0, "fast": 0.25, "normal": 0.7, "slow": 1.2}
DIFFICULTIES = ("easy", "normal", "hard")


class Settings:
    def __init__(self):
        self.text_speed = "normal"
        self.colors = True
        self.ai_difficulty = "normal"
        self.show_descriptions = True
        self.show_dialogue = True

    @property
    def pause_time(self):
        return TEXT_SPEEDS[self.text_speed]

    def load(self):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        if data.get("text_speed") in TEXT_SPEEDS:
            self.text_speed = data["text_speed"]
        if data.get("ai_difficulty") in DIFFICULTIES:
            self.ai_difficulty = data["ai_difficulty"]
        if isinstance(data.get("colors"), bool):
            self.colors = data["colors"]
        if isinstance(data.get("show_descriptions"), bool):
            self.show_descriptions = data["show_descriptions"]
        if isinstance(data.get("show_dialogue"), bool):
            self.show_dialogue = data["show_dialogue"]

    def save(self):
        data = {
            "text_speed": self.text_speed,
            "colors": self.colors,
            "ai_difficulty": self.ai_difficulty,
            "show_descriptions": self.show_descriptions,
            "show_dialogue": self.show_dialogue,
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            print("(Could not save settings.)")


settings = Settings()
settings.load()
 