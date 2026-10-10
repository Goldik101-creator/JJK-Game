from ui import ask_int, move_menu, paint, say, show_status, stat_card
 
MAX_TURNS = 32

def focus_index(f):
    for i, move in enumerate(f.moves):
        if move.name == "Focus":
            return i
    return 0
 
 
def ai_turn(f, e):
    choice = f.choose_move(e)
    if choice == "focus":
        choice = focus_index(f)
    if not f.attack(e, choice):
        f.attack(e, focus_index(f))
 
 
def human_turn(f, e):
    while True:
        move_menu(f)
        choice = ask_int(f"{f.name}, choose a move: ", 1, len(f.moves), extras=("i",))
        if choice == "i":
            print(stat_card(e))
            continue
        if f.attack(e, choice - 1):
            return
 
 
def start_of_turn(f, e):
    f.apply_status_effect(e)
    if not f.is_alive() or not e.is_alive():
        return False
    if f.frozen:
        say(paint(f"\n{f.name} is frozen and cannot move!", "cyan"))
        f.frozen = False
        return False
    return True
 
 
def end_of_turn(f, just_used):
    for name in f.cooldown:
        if f.cooldown[name] > 0 and name not in just_used:
            f.cooldown[name] -= 1
    f.reduce_domain()
    f.reduce_simple_domain()
    if f.max_ce > 0:
        f.regain_ce()
 
 
def play_turn(f, e):
    just_used = set()
    if start_of_turn(f, e):
        before = dict(f.cooldown)
        if f.ai:
            ai_turn(f, e)
        else:
            human_turn(f, e)
        just_used = {n for n, cd in f.cooldown.items() if cd > before.get(n, 0)}
    if f.is_alive():
        end_of_turn(f, just_used)
 
 
def run_battle(p1, p2, max_turns=MAX_TURNS):
    turns = 0
    while p1.is_alive() and p2.is_alive() and turns < max_turns:
        turns += 1
        print(paint(f"\n{'─' * 22} Turn {turns} {'─' * 22}", "cyan"))
        for attacker, defender in ((p1, p2), (p2, p1)):
            if not (attacker.is_alive() and defender.is_alive()):
                break
            show_status(p1, p2)
            play_turn(attacker, defender)
    if p1.is_alive() and not p2.is_alive():
        return 0, turns
    if p2.is_alive() and not p1.is_alive():
        return 1, turns
    return None, turns