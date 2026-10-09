import os
import re
import textwrap
import time
 
from descriptions import describe
from settings import settings
 
ANSI = {
    "reset": "\033[0m", "bold": "\033[1m",
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
    "white": "\033[97m", "gray": "\033[90m",
}
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")
 
HP_SCALE = 180  # highest max HP in the roster (for stat card bars)
CE_SCALE = 151  # highest max CE in the roster
 
 
def enable_ansi():
    if os.name == "nt":
        os.system("")
 
 
def paint(text, color=None, bold=False):
    if not settings.colors or (color is None and not bold):
        return str(text)
    prefix = (ANSI["bold"] if bold else "") + (ANSI[color] if color else "")
    return f"{prefix}{text}{ANSI['reset']}"
 
 
def visible_len(text):
    return len(_ANSI_RE.sub("", text))
 
 
def pause():
    delay = settings.pause_time
    if delay > 0:
        time.sleep(delay)
 
 
def say(text):
    pause()
    print(text)
 
 

def bar(current, maximum, width=20, color=None):
    maximum = max(1, maximum)
    ratio = max(0.0, min(1.0, current / maximum))
    filled = round(ratio * width)
    if current > 0 and filled == 0:
        filled = 1
    if color is None:
        color = "green" if ratio > 0.5 else "yellow" if ratio > 0.25 else "red"
    if settings.colors:
        body = paint("█" * filled, color) + paint("░" * (width - filled), "gray")
    else:
        body = "#" * filled + "-" * (width - filled)
    return f"[{body}]"
 
 
def status_tags(f):
    tags = []
    if f.burn_turns > 0:
        tags.append(paint(f"Burning({f.burn_turns})", "red"))
    if f.frozen:
        tags.append(paint("Frozen", "cyan"))
    if f.domain_active:
        tags.append(paint(f"Domain: {f.domain_name} ({f.domain_turns})", "magenta"))
    if f.simple_domain:
        tags.append(paint(f"Simple Domain ({f.simple_domain_turns})", "blue"))
    if f.blood_stack:
        tags.append(paint(f"Blood x{f.blood_stack}", "red"))
    if f.speed_stack:
        tags.append(paint(f"Speed x{f.speed_stack}", "yellow"))
    if f.overtime:
        tags.append(paint("Overtime", "yellow"))
    if f.boogie_woogie_dodge:
        tags.append(paint("Swap ready", "green"))
    return tags
 
 
def fighter_panel(f):
    lines = [paint(f.name, "white", bold=True) + paint(f'  "{f.title}"', "gray")]
    lines.append(f"  HP {bar(f.hp, f.max_hp, 24)} {f.hp}/{f.max_hp}")
    if f.max_ce > 0:
        lines.append(f"  CE {bar(f.ce, f.max_ce, 24, 'cyan')} {f.ce}/{f.max_ce}")
    else:
        lines.append("  CE " + paint("none (Heavenly Restriction)", "gray"))
    tags = status_tags(f)
    if tags:
        lines.append("  " + " | ".join(tags))
    return lines
 
 
def show_status(p1, p2):
    print()
    for line in fighter_panel(p1):
        print(line)
    print(paint("          ── VS ──", "gray"))
    for line in fighter_panel(p2):
        print(line)
 
 

def box(lines, width=66, title=None):
    inner = width - 2
    if title:
        top = "╔" + f" {title} ".center(inner, "═") + "╗"
    else:
        top = "╔" + "═" * inner + "╗"
    out = [top]
    for line in lines:
        pad = max(0, inner - 2 - visible_len(line))
        out.append("║ " + line + " " * pad + " ║")
    out.append("╚" + "═" * inner + "╝")
    return "\n".join(out)
 
 
def move_label(move):
    if move.is_domain:
        return "Domain"
    if move.damage < 0:
        return f"Heal {-move.damage}"
    if move.damage > 0:
        return f"Damage {move.damage}"
    return "Utility"
 
 
def stat_card(f, width=66):
    inner = width - 4
    lines = [paint(f.name, "yellow", bold=True) + paint(f'  "{f.title}"', "gray"), ""]
    lines.append(f"HP  {bar(f.max_hp, HP_SCALE, 20, 'green')} {f.max_hp}")
    if f.max_ce > 0:
        lines.append(f"CE  {bar(f.max_ce, CE_SCALE, 20, 'cyan')} {f.max_ce}")
    else:
        lines.append("CE  " + paint("none (Heavenly Restriction)", "gray"))
    lines.append("")
    lines.append(paint("Passive / Tip", "yellow"))
    for chunk in textwrap.wrap(f.tip, inner):
        lines.append(chunk)
    lines.append("")
    lines.append(paint("Moves", "yellow"))
    for i, m in enumerate(f.moves, 1):
        lines.append(f"{i}. {m.name:<30} {move_label(m):<10} CE {m.ce_cost:<3} CD {m.cooldown}")
        if settings.show_descriptions:
            for chunk in textwrap.wrap(describe(m), inner - 3):
                lines.append("   " + paint(chunk, "gray"))
    return "\n" + box(lines, width)
 
 
def move_menu(f):
    print(paint(f"\n{f.name}'s moves", "yellow", bold=True) + f"   HP {f.hp}/{f.max_hp} | CE {f.ce}/{f.max_ce}")
    for i, m in enumerate(f.moves, 1):
        cd = f.cooldown[m.name]
        if cd > 0:
            status = f"CD {cd}"
        elif f.ce < m.ce_cost:
            status = "no CE"
        else:
            status = "ready"
        row = f"{i}. {m.name:<30} {move_label(m):<10} CE {m.ce_cost:<3} {status}"
        print(paint(row, None if status == "ready" else "gray"))
        if settings.show_descriptions:
            print("     " + paint(describe(m), "gray"))
    print(paint("(type 'i' to inspect your opponent)", "gray"))
 
 

def ask_int(prompt, lo, hi, extras=()):
    while True:
        raw = input(prompt).strip().lower()
        if raw in extras:
            return raw
        if raw.isdigit() and lo <= int(raw) <= hi:
            return int(raw)
        print("Invalid choice, try again.")
 
 
def ask_number(prompt, lo, hi, default):
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()
        if raw == "":
            return default
        if raw.isdigit() and lo <= int(raw) <= hi:
            return int(raw)
        print(f"Enter a number from {lo} to {hi}.")
 
 
def confirm(prompt):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer y or n.")