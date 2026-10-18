import random

import stats
from battle import run_battle
from dialogue import draw_dialogue, intro_dialogue, victory_dialogue
from roster import ROSTER
from settings import DIFFICULTIES, TEXT_SPEEDS, settings
from ui import ask_int, confirm, enable_ansi, paint, say, stat_card

MODES = {
    1: ("Human vs AI", (True, False)),
    2: ("Human vs Human", (True, True)),
    3: ("AI vs AI", (False, False)),
}

def select_character(label):
    previews = [cls() for cls in ROSTER]
    while True:
        print(paint(f"\n{label}: choose a fighter", "yellow", bold=True))
        for i, p in enumerate(previews, 1):
            print(f" {i:>2}. {p.name:<18} HP {p.max_hp:<4} CE {p.max_ce:<4} " + paint(p.title, "gray"))
        choice = ask_int("Number to preview, or 'r' for random: ", 1, len(previews), extras=("r",))
        if choice == "r":
            fighter = random.choice(ROSTER)()
            print(f"Random pick: {paint(fighter.name, 'yellow', bold=True)}")
            return fighter
        print(stat_card(previews[choice - 1]))
        if confirm("Pick this fighter? (y/n): "):
            return ROSTER[choice - 1]()

def ask_name(default):
    name = input(f"{default} name (blank for '{default}'): ").strip()
    return name or default


def play_game():
    print(paint("\nGame modes", "yellow", bold=True))
    for number, (label, _) in MODES.items():
        print(f" {number}. {label}")
    mode = ask_int("Choose a mode: ", 1, len(MODES))
    mode_name, (human1, human2) = MODES[mode]

    name1 = ask_name("Player 1") if human1 else None
    name2 = ask_name("Player 2") if human2 else None
    if human1 and human2 and name1.lower() == name2.lower():
        name2 = name2 + " (2)"

    label1 = name1 or ("AI 1" if mode == 3 else "AI")
    label2 = name2 or ("AI 2" if mode == 3 else "AI")
    cls1 = type(select_character(label1))
    cls2 = type(select_character(label2))

    data = stats.load()
    while True:
        p1, p2 = cls1(), cls2()
        p1.ai = not human1
        p2.ai = not human2

        intro_dialogue(p1, p2)
        winner, turns = run_battle(p1, p2)

        if winner is None:
            draw_dialogue(p1, p2)
        else:
            victory_dialogue((p1, p2)[winner], (p1, p2)[1 - winner])
        print(paint(f"Match length: {turns} turns", "gray"))

        if human1 or human2:
            stats.record_match(data, [
                {"player": name1, "character": p1.name},
                {"player": name2, "character": p2.name},
            ], winner)

        if not confirm("\nRematch with the same fighters? (y/n): "):
            return


def show_stats():
    data = stats.load()
    if data["matches"] == 0:
        print(paint("\nNo matches recorded yet. Play a Human vs AI or Human vs Human game first.", "gray"))
        return
    print(paint(f"\nStats  ({data['matches']} matches recorded)", "yellow", bold=True))

    if data["players"]:
        print(paint("\nPlayers", "yellow"))
        print(f"  {'Name':<16} {'W-L-D':<10} {'Win %':>6}   Favorite fighter")
        ranked = sorted(data["players"].items(), key=lambda kv: (-stats.win_rate(kv[1]), kv[0]))
        for name, e in ranked:
            record = f"{e['wins']}-{e['losses']}-{e['draws']}"
            print(f"  {name:<16} {record:<10} {stats.win_rate(e):>5.1f}%   {stats.favorite(e)}")

    if data["characters"]:
        print(paint("\nFighters", "yellow"))
        print(f"  {'Fighter':<18} {'W-L-D':<10} {'Win %':>6}")
        ranked = sorted(data["characters"].items(), key=lambda kv: (-stats.win_rate(kv[1]), kv[0]))
        for name, e in ranked:
            record = f"{e['wins']}-{e['losses']}-{e['draws']}"
            print(f"  {name:<18} {record:<10} {stats.win_rate(e):>5.1f}%")


def on_off(value):
    return paint("ON", "green") if value else paint("OFF", "red")


def cycle(options, current):
    options = list(options)
    return options[(options.index(current) + 1) % len(options)]


def settings_menu():
    while True:
        print(paint("\nSettings", "yellow", bold=True))
        print(f" 1. Text speed         : {settings.text_speed}")
        print(f" 2. Colors             : {on_off(settings.colors)}")
        print(f" 3. AI difficulty      : {settings.ai_difficulty}")
        print(f" 4. Move descriptions  : {on_off(settings.show_descriptions)}")
        print(f" 5. Pre-battle dialogue : {on_off(settings.show_dialogue)}")
        print(" 6. Reset saved stats")
        print(" 7. Back")
        choice = ask_int("Choose an option (1-5 toggles it): ", 1, 7)
        if choice == 1:
            settings.text_speed = cycle(TEXT_SPEEDS, settings.text_speed)
        elif choice == 2:
            settings.colors = not settings.colors
        elif choice == 3:
            settings.ai_difficulty = cycle(DIFFICULTIES, settings.ai_difficulty)
        elif choice == 4:
            settings.show_descriptions = not settings.show_descriptions
        elif choice == 5:
            settings.show_dialogue = not settings.show_dialogue
        elif choice == 6:
            if input("Type YES to erase all saved stats: ").strip() == "YES":
                stats.reset()
                print("Stats erased.")
            continue
        else:
            return
        settings.save()

def main():
    enable_ansi()
    print(paint("\n=== JUJUTSU KAISEN: CLASH OF SORCERERS ===", "magenta", bold=True))
    while True:
        print(paint("\nMain menu", "yellow", bold=True))
        print(" 1. Play")
        print(" 2. Stats")
        print(" 3. Settings")
        print(" 4. Quit")
        choice = ask_int("Choose an option: ", 1, 4)
        if choice == 1:
            play_game()
        elif choice == 2:
            show_stats()
        elif choice == 3:
            settings_menu()
        else:
            print("Thanks for playing!")
            return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nThanks for playing!")