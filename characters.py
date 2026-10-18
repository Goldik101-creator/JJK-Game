import random

from moves import Move
from output import out
from settings import settings
from ui import say, pause, paint
from utilities import safe_int_input

DOMAIN_MOVES = [
    "Malevolent Shrine", "Unlimited Void", "Chimera Shadow Garden",
    "Celestial Star Forge", "Authentic Mutual Love", "Womb Profusion",
    "Self-Embodiment of Perfection", "Coffin of The Iron Mountain",
    "Benevolent Shrine", "Time Cell Moon Palace",
]
CANNOT_DODGE_DOMAINS = [d for d in DOMAIN_MOVES if d != "Benevolent Shrine"]
UNDODGEABLE_MOVES = {"Inverted Spear Of Heaven", "Soul Split Katana Slash"}

# AI difficulty: chance (%) of picking a random move instead of the strongest,
# and the (enemy HP, own HP) limits under which the AI opens its domain
RANDOM_MOVE_CHANCE = {"easy": 60, "normal": 25, "hard": 5}
DOMAIN_THRESHOLDS = {"easy": (40, 40), "normal": (70, 60), "hard": (110, 90)}

# A window can set this to a function(fighter, options) that lets a human pick a Call to Rika technique
RIKA_CHOOSER = None

# These end the match in a draw, so the AI only uses them when it is losing
STALEMATE_MOVES = ("Divine General MAHORAGA", "Black Hole")

# (low, high) of a 0-100 roll that counts as a dodge
DEFAULT_DODGE = (52, 58)
DODGE_RANGES = {
    "Toji Fushiguro": (45, 65),
    "Maki Zenin": (47, 63),
    "Satoru Gojo": (47, 63),
}

YUTA_TECHNIQUES = {
    "Limitless": (6, 4),
    "Dismantle": (6, 4),
    "Ice Breaker": (4, 6),
    "Cursed Speech": (4, 6),
    "Jacob's Ladder": (2, 9),
}

DOMAIN_EFFECTS = {
    "Malevolent Shrine": "_domain_malevolent_shrine",
    "Chimera Shadow Garden": "_domain_chimera_shadow_garden",
    "Authentic Mutual Love": "_domain_authentic_mutual_love",
    "Celestial Star Forge": "_domain_celestial_star_forge",
    "Womb Profusion": "_domain_womb_profusion",
    "Self-Embodiment of Perfection": "_domain_self_embodiment",
    "Coffin of The Iron Mountain": "_domain_coffin",
    "Benevolent Shrine": "_domain_benevolent_shrine",
    "Time Cell Moon Palace": "_domain_time_cell",
}



for _domain, _handler in (("Idle Death Gamble", "_domain_idle_death_gamble"),
                          ("Deadly Sentencing", "_domain_deadly_sentencing")):
    DOMAIN_MOVES.append(_domain)
    CANNOT_DODGE_DOMAINS.append(_domain)  # guaranteed hits like most domains
    DOMAIN_EFFECTS[_domain] = _handler

# Utility moves and commands that shouldn't be dodgeable
UNDODGEABLE_MOVES.update({"Summon Crows", "Stop!"})


class Jjk:
    number = 0  # how many fighters have been created

    def __init__(self, name, hp, ce, tip, title, soul_attack=False):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.ce = ce
        self.max_ce = ce
        self.tip = tip
        self.title = title
        self.soul_attack = soul_attack
        self.ai = True

        self.moves = []
        self.cooldown = {}

        # domain / simple domain
        self.domain_active = False
        self.domain_turns = 0
        self.domain_name = ""
        self.simple_domain = False
        self.simple_domain_turns = 0

        # status effects and character-specific state
        self.burn_turns = 0
        self.burn_damage = 0
        self.blood_stack = 0
        self.frozen = False
        self.speed_stack = 0
        self.projection_active = False
        self.boogie_woogie_dodge = False
        self.overtime = False
        self.chill = 0  # from Uraume's attacks
        self.flash_streak = 0  # Yuji's Black Flash zone

        Jjk.number += 1

    def __str__(self):
        return self.name

    def is_alive(self):
        return self.hp > 0

    # Hooks: a character overrides these to get a unique mechanic
    def on_turn_tick(self, _enemy):
        """Runs once at the start of this fighter's turn (from apply_status_effect)."""

    def on_hit(self, _enemy, _move):
        """Runs when one of this fighter's attacks lands (after dodges)."""

    def modify_outgoing(self, _enemy, _move, damage):
        """Adjust the damage this fighter deals. Return the new damage."""
        return damage

    def modify_incoming(self, _attacker, _move, damage):
        """Adjust the damage this fighter takes. Return the new damage."""
        return damage

    # attribute name -> (label, color) for the status panel. Subclasses add their own.
    STATUS = {"chill": ("Chill", "cyan")}

    def extra_status(self):
        """Tags for the status panel, e.g. [("Crows x3", "white")]."""
        tags = []
        for attr, (label, color) in {**Jjk.STATUS, **self.STATUS}.items():
            value = getattr(self, attr, 0)
            if value is True:
                tags.append((label, color))
            elif value:
                tags.append((f"{label} x{value}", color))
        return tags

    def return_num_moves(self):
        return len(self.moves) - 1

    def spend_ce(self, amount):
        self.ce = max(0, self.ce - amount)

    def gain_hp(self, amount):
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def add_moves(self, move, start_cd=0):
        self.moves.append(move)
        self.cooldown[move.name] = start_cd

    def show_moves(self):
        out(f"{self.name} HP: {self.hp} | CE: {self.ce}/{self.max_ce}")
        for i, move in enumerate(self.moves, 1):
            pause()
            out(f"{i}. {move.name} |Damage: {move.damage}| CE cost: {move.ce_cost} "
                  f"| Cooldown: {self.cooldown[move.name]}")

    def on_cooldown(self, move):
        if self.cooldown[move.name] > 0:
            out(f"\n{move.name} is on cooldown! Choose another move. ")
            return True
        return False

    def _finish_move(self, move):
        self.spend_ce(move.ce_cost)
        self.cooldown[move.name] = move.cooldown

    def focus_ce(self):
        gain = random.randint(20, 35)
        self.ce = min(self.ce + gain, self.max_ce)
        out(f"\n{self.name} focused and regained {gain} CE")

    def regain_ce(self):
        regain = random.randint(2, 8)
        self.ce = min(self.ce + regain, self.max_ce)
        say(f"\n{self.name} regained {regain} CE")

    def reduce_cooldown(self):
        for move_name in self.cooldown:
            if self.cooldown[move_name] > 0:
                self.cooldown[move_name] -= 1

    def apply_status_effect(self, enemy):
        if enemy.is_alive():
            self.on_turn_tick(enemy)
        if enemy.is_alive() and self.burn_turns > 0:
            say(paint(f"\n{self.name} is burning", "red"))
            self.hp = max(0, self.hp - self.burn_damage)
            say(paint(f"{self.name} took {self.burn_damage} burn damage", "red"))
            out(f"{self.name} is at {self.hp} HP")
            self.burn_turns -= 1

    def activate_domain(self, domain_name, turns):
        self.domain_active = True
        self.domain_turns = turns
        self.domain_name = domain_name
        out(f"\n{self.name} opened their domain: ")
        say(paint(domain_name, "magenta", bold=True))

    def reduce_domain(self):
        if self.domain_active:
            self.domain_turns -= 1
            if self.domain_turns <= 0:
                out(f"\n{self.domain_name} faded away...")
                self.domain_active = False
                self.domain_name = ""

    def activate_simple_domain(self, turns):
        self.simple_domain = True
        self.simple_domain_turns = turns
        out(f"\n{self.name} activated New Shadow Style Technique: Simple Domain")
        say(f"{self.name} neutralizes techniques around them.")

    def reduce_simple_domain(self):
        if self.simple_domain:
            self.simple_domain_turns -= 1
            if self.simple_domain_turns <= 0:
                out(f"{self.name}'s simple domain shattered")
                self.simple_domain = False

    def _yuta_technique_bonus(self, message, index):
        out(message)
        choice = random.choice(list(YUTA_TECHNIQUES))
        out(choice)
        return YUTA_TECHNIQUES[choice][index]

    def heal(self, move):
        amount = max(0, random.randint(-move.damage - 5, -move.damage + 5))
        out(f"\n{self.name} used {move.name}")
        if self.domain_name == "Authentic Mutual Love":
            amount += 4 + self._yuta_technique_bonus(
                f"\n{self.name} gets healed by one of these techniques: ", 1)
        healed = self.gain_hp(amount)
        say(paint(f"\n{self.name} healed {healed} hp", "green"))
        say(f"{self.name} is at {self.hp} hp")
        self._finish_move(move)
        return True

    def suicide_move(self, enemy, move):
        enemy.hp = 0
        self.hp = 0
        out(f"\n{self.name} used {move.name}")
        say(f"\n{enemy.name} is at {enemy.hp} hp")
        say(f"{self.name} is at {self.hp} hp")
        say(f"{self.name} destroyed the Battlefield")
        self.spend_ce(move.ce_cost)


    def _rika_moves(self):
        return [
            Move("Cleave and Dismantle", 30, 0, 0),
            Move("Hollow Purple", 40, 0, 0, crit=2, soul_resistence=True),
            Move("Jacob's Ladder", -25, 0, 0),
            Move("Cursed Speech", 23, 0, 0),
            Move("Black Flash", 35, 0, 0, crit=2, soul_resistence=True),
        ]

    def _choose_rika_move(self, options):
        if RIKA_CHOOSER is not None:
            return RIKA_CHOOSER(self, options)
        out("\nChoose a move:")
        for i, move in enumerate(options, 1):
            out(f"{i}. {move.name} | Damage: {move.damage}")
            pause()
        while True:
            choice = safe_int_input("Choose the move: ")
            if 1 <= choice <= len(options):
                return options[choice - 1]
            out("Invalid move.")

    def _pick_rika_move_ai(self, enemy, options):
        attacks = [m for m in options if m.damage >= 0]
        heals = [m for m in options if m.damage < 0]
        best = max(attacks, key=lambda m: m.damage)
        if self.hp <= 25:
            if enemy.hp < 30:
                return best
            if heals:
                return random.choice(heals)
        if random.randint(1, 100) <= 25:  # a little randomness
            return random.choice(attacks)
        return best

    def call_to_rika(self, enemy, cooldown, ce_cost):
        options = self._rika_moves()
        if self.ai:
            move = self._pick_rika_move_ai(enemy, options)
        else:
            move = self._choose_rika_move(options)

        if move.damage < 0:
            self.heal(move)
        else:
            self.damage_attack(enemy, move)  # damage_attack handles dodging

        self.cooldown["Call to Rika"] = cooldown
        self.spend_ce(ce_cost)
        return True

    def _dodge_message(self, enemy, move):
        roll = random.randint(0, 100)

        if enemy.boogie_woogie_dodge and 35 <= roll <= 75:
            enemy.boogie_woogie_dodge = False
            return f"{enemy.name} swapped positions with Boogie Woogie and dodged!"

        if enemy.domain_name == "Time Cell Moon Palace" and 35 <= roll <= 75:
            return f"{enemy.name} moved through frames and dodged!"

        if enemy.name == "Naoya Zenin" and enemy.speed_stack >= 1:
            low = max(0, 52 - enemy.speed_stack)
            high = min(100, 58 + enemy.speed_stack)
            if low <= roll <= high:
                return f"{enemy.name} moved at impossible speeds, and dodged!"

        low, high = DODGE_RANGES.get(enemy.name, DEFAULT_DODGE)
        if low <= roll <= high:
            if enemy.name == "Satoru Gojo":
                return f"{enemy.name} dodged {move.name} with infinity"
            return f"{enemy.name} dodged {move.name}"
        return None

    def handle_dodge(self, enemy, move):
        message = self._dodge_message(enemy, move)
        if message is None:
            return False
        out(f"\n{self.name} used {move.name}")
        say(paint(message, "cyan"))
        self._finish_move(move)
        return True

    def _domain_malevolent_shrine(self, enemy, damage):
        out(f"\n{enemy.name} gets cleaved and dismantled by the Shrine")
        return int(damage * 1.225)

    def _domain_chimera_shadow_garden(self, enemy, damage):
        out(f"\n{enemy.name} gets lost in the shadows and got attacked by some clones")
        return int(damage * 1.225) + random.randint(4, 10)

    def _domain_authentic_mutual_love(self, enemy, damage):
        bonus = self._yuta_technique_bonus(
            f"\n{enemy.name} gets hit by one of these techniques: ", 0)
        return damage + 4 + bonus

    def _domain_celestial_star_forge(self, enemy, damage):
        out(f"\n{enemy.name} gets crushed under the Star")
        self.hp = max(0, self.hp - 4)
        out(f"\n{self.name} gets damaged from her innate technique inside the domain, health: {self.hp}")
        return int(damage * 1.2) + 7

    def _domain_womb_profusion(self, _enemy, damage):
        out(f"\n{self.name} creates a tree of grotesque human faces...")
        return damage + 12

    def _domain_self_embodiment(self, _enemy, damage):
        out(f"\n{self.name} shows the embodiment of his Perfection...")
        self.gain_hp(random.randint(7, 15))
        out(f"{self.name} heals himself within the domain...\n{self.name} is at {self.hp} hp")
        return damage + 10

    def _domain_coffin(self, _enemy, damage):
        out("\nA Large Mountain spews lava. It is getting extremely hot")
        return max(int(damage * 1.5) - 6, 0)

    def _domain_benevolent_shrine(self, _enemy, damage):
        out("\nHappy memories flood the domain.")
        self.gain_hp(12)
        out(f"{self.name} heals his soul from the domain, {self.hp} hp")
        return max(int(damage * 1.65 - 9), 0)

    def _domain_time_cell(self, enemy, damage):
        out(f"\n{enemy.name}'s cells are forced into frames!")
        if random.randint(1, 100) <= 45:
            enemy.frozen = True
            out(f"{enemy.name} failed to follow the 24 FPS rule and froze!")
        return damage + self.speed_stack * 5

    def _check_overtime(self):
        if self.name == "Kento Nanami" and not self.overtime and self.hp <= self.max_hp // 2:
            self.overtime = True
            say(paint("\nNanami entered Overtime...", "yellow", bold=True))

    def _roll_damage(self, move):
        low_roll = 1 if self.name == "Kento Nanami" else 0  # Nanami crits more often
        is_crit = random.randint(low_roll, 10) == 10
        damage = max(0, random.randint(move.damage - 3, move.damage + 3))
        if is_crit:
            damage = int(damage * move.crit)
        return damage, is_crit

    def _apply_on_hit_effects(self, enemy, move):
        if move.name == "Projection Sorcery":
            self.projection_active = True
            self.speed_stack += 1
            out(f"{self.name} accelerated with Projection sorcery!")

        if move.freeze and random.randint(0, 100) <= 45:
            enemy.frozen = True

        if self.name == "Choso Kamo" and move.blood:
            enemy.blood_stack += 1
            out(f"\n{enemy.name} gained a Blood Stack!")
            out(f"Blood Stacks: {enemy.blood_stack}")

        if move.name == "Boogie Woogie":
            self.boogie_woogie_dodge = True
            say(f"\n{self.name} becomes unpredictable with {move.name}")

        if move.burn and random.randint(1, 100) <= 39:
            enemy.burn_turns = 2
            enemy.burn_damage = 8
            out(f"\n{enemy.name} was burned!")

        self.on_hit(enemy, move)

    def _apply_attacker_bonuses(self, enemy, move, damage):
        if self.name == "Toji Fushiguro" and enemy.domain_active:
            damage += 15
            out("Toji Fushiguro gets mildly affected by the domain.")

        if self.name == "Maki Zenin" and self.hp <= self.max_hp / 2:
            damage += 5
            out("Maki Zenin enters a rage mode.")

        handler = DOMAIN_EFFECTS.get(self.domain_name)
        if handler:
            damage = getattr(self, handler)(enemy, damage)

        if move.name == "Supernova":
            damage += enemy.blood_stack * 6
            say(f"\nSupernova exploded {enemy.blood_stack} blood stacks!")
            enemy.blood_stack = 0

        if self.projection_active:
            damage += self.speed_stack * 5

        if self.name == "Kento Nanami":
            if self.overtime:
                damage += 5
            if move.name in ("Ratio Technique", "Collapsed Strike") and random.randint(1, 100) <= 45:
                out("\nNanami struck the 7:3 weak point!")
                damage += 5

        if self.chill:
            damage = int(damage * (1 - 0.04 * self.chill))

        return self.modify_outgoing(enemy, move, damage)

    def _apply_defender_reductions(self, enemy, move, damage):
        if enemy.domain_name == "Unlimited Void":
            damage = max(damage // 2, 0)
            out(f"{self.name} is stunned with infinite knowledge")

        if enemy.domain_name == "Chimera Shadow Garden":
            damage = max(damage // 3, 0)
            out(f"\nShadows are taking over {self.name}")

        if enemy.simple_domain:
            if self.domain_active:
                out(f"\n{enemy.name}'s Simple Domain disrupts the guaranteed-hit effect!")
                damage = int(damage * 0.5)
            else:
                say(f"\n{enemy.name}'s Simple Domain weakens the attack")
                damage = int(damage * 0.65)

        if enemy.soul_attack and not move.soul_resistence:
            say(f"\n{self.name}'s attack was ineffective against {enemy.name} due to {enemy.name}'s soul resistance.")
            damage = int(damage * 0.89)

        if enemy.name == "Kenjaku" and damage >= 30 and random.randint(1, 100) <= 39:
            damage = int(damage * 0.65)
            say("\nKenjaku used Anti-Gravity System to lessen the impact!")

        return enemy.modify_incoming(self, move, damage)

    def _deal_damage(self, enemy, damage):
        enemy.hp = max(0, enemy.hp - damage)
        say(paint(f"{enemy.name} took {damage} damage", "red"))
        say(f"{enemy.name} is at {enemy.hp} hp")

    def damage_attack(self, enemy, move, can_dodge=True):
        # Opening a domain does no damage
        if move.is_domain:
            self.activate_domain(move.name, 4)
            self._finish_move(move)
            return True

        if move.name in UNDODGEABLE_MOVES or move.name in CANNOT_DODGE_DOMAINS:
            can_dodge = False
        if can_dodge and self.handle_dodge(enemy, move):
            return True

        self._check_overtime()
        damage, is_crit = self._roll_damage(move)
        if is_crit:
            out(paint(f"\n{self.name} entered the zone and hit a critical {move.name}", "yellow", bold=True))
        else:
            out(f"\n{self.name} used {move.name}")

        self._apply_on_hit_effects(enemy, move)
        damage = self._apply_attacker_bonuses(enemy, move, damage)
        damage = self._apply_defender_reductions(enemy, move, damage)
        self._deal_damage(enemy, damage)
        self._finish_move(move)
        return True

    def attack(self, enemy, move_index):
        move = self.moves[move_index]

        if move.name == "Focus":
            self.focus_ce()
            return True
        if self.ce < move.ce_cost:
            out(f"\nNot enough Cursed Energy for {move.name}")
            return False
        if self.on_cooldown(move):
            return False

        if move.name == "Simple Domain":
            self.activate_simple_domain(3)
            self._finish_move(move)
            return True
        if move.damage < 0:
            return self.heal(move)
        if move.name in ("Divine General MAHORAGA", "Black Hole"):
            self.suicide_move(enemy, move)
            return True
        if move.name == "Call to Rika":
            return self.call_to_rika(enemy, move.cooldown, move.ce_cost)
        return self.damage_attack(enemy, move)

    def _ai_value(self, move, enemy):
        if move.name == "Supernova":
            return move.damage + enemy.blood_stack * 6
        if move.name == "Call to Rika":
            return 38
        if move.name == "Projection Sorcery":
            return max(0, 34 - self.speed_stack * 9)
        return move.damage

    def choose_move(self, enemy):
        if self.name not in ("Toji Fushiguro", "Maki Zenin") and self.ce <= 15:
            return "focus"

        losing = self.hp <= 45 and self.hp < enemy.hp
        available = [
            (i, move) for i, move in enumerate(self.moves)
            if self.cooldown[move.name] == 0 and self.ce >= move.ce_cost
            and (losing or move.name not in STALEMATE_MOVES)
        ]
        if not available:
            return "focus"

        def strongest():
            return max(available, key=lambda pair: self._ai_value(pair[1], enemy))[0]

        if self.hp <= 25:
            if enemy.hp < 30:
                return strongest()  # go for the kill
            heals = [pair for pair in available if pair[1].damage < 0]
            if heals:
                return random.choice(heals)[0]

        stalemates = [pair for pair in available if pair[1].name in STALEMATE_MOVES]
        if stalemates and random.randint(1, 100) <= 50:
            return stalemates[0][0]  # losing anyway: take the enemy down with us

        domain_enemy_hp, domain_own_hp = DOMAIN_THRESHOLDS[settings.ai_difficulty]
        for i, move in available:
            if move.name in DOMAIN_MOVES and enemy.hp <= domain_enemy_hp and self.hp <= domain_own_hp:
                return i

        if random.randint(1, 100) <= RANDOM_MOVE_CHANCE[settings.ai_difficulty]:
            return random.choice(available)[0]
        return strongest()


class Yuji(Jjk):
    STATUS = {**Jjk.STATUS, "flash_streak": ("Zone", "yellow")}

    def __init__(self):
        super().__init__("Yuji Itadori", 178, 103,
                         "Black Flashes have a 10 percent chance to do double damage, and each Black Flash that lands adds +4 damage to the next ones (max +12). Simple Domain nullifies a chunk of damage.",
                         "The Strongest of The Future")
        self.add_moves(Move("Divergent Fist", 17, 0, 10, soul_resistence=True), start_cd=0)
        self.add_moves(Move("Black Flash", 35, 2, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Cleave and Dismantle", 22, 1, 20), start_cd=2)
        self.add_moves(Move("Blood Manipulation", 25, 3, 20), start_cd=2)
        self.add_moves(Move("Reverse Cursed Technique", -20, 3, 20), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Benevolent Shrine", 0, 5, 50, is_domain=True), start_cd=5)

    def modify_outgoing(self, _enemy, move, damage):
        # BALANCE/REWORK: each Black Flash that lands deepens the zone: +4 damage per previous one (max +12)
        if move.name == "Black Flash":
            if self.flash_streak:
                damage += self.flash_streak * 4
                out(f"{self.name} is in the zone! (+{self.flash_streak * 4} damage)")
            self.flash_streak = min(3, self.flash_streak + 1)
        return damage


class Gojo(Jjk):
    def __init__(self):
        super().__init__("Satoru Gojo", 133, 140,
                         "Gojo has a 17 percent chance of dodging. Hollow Purple and Black Flash has a 10 percent chance to do double the damage. Simple Domain nullifies a chunk of damage.",
                         "The Honored One")
        self.add_moves(Move("Blue", 20, 0, 15, soul_resistence=True), start_cd=0)
        self.add_moves(Move("Red", 30, 2, 25, soul_resistence=True), start_cd=1)
        self.add_moves(Move("Hollow Purple", 40, 3, 45, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Reverse Cursed Technique", -20, 3, 25), start_cd=1)
        self.add_moves(Move("Black Flash", 35, 3, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Unlimited Void", 0, 5, 45, is_domain=True), start_cd=5)


class Choso(Jjk):
    def __init__(self):
        super().__init__("Choso Kamo", 160, 93,
                         "Save his blood stacks for supernova as the blood stacks can EXPLODE with Supernova dealing extra burst damage.",
                         "The Blood Brother")
        self.add_moves(Move("Convergence", 20, 0, 15, blood=True), start_cd=0)
        self.add_moves(Move("Piercing Blood", 23, 2, 17, blood=True), start_cd=2)
        self.add_moves(Move("Supernova", 24, 3, 20), start_cd=2)
        self.add_moves(Move("Slicing Exorcism", 31, 3, 21, blood=True), start_cd=3)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)


class Maki(Jjk):
    def __init__(self):
        super().__init__("Maki Zenin", 122, 0,
                         "Soul Split Katana Slash cannot be dodged. She has extra damage when in low health. Domains hit her 20 percent harder.",
                         "Zero Cursed Energy Empress")
        self.add_moves(Move("Polearms hit", 19, 0, 0), start_cd=0)
        self.add_moves(Move("Mai's Wrath", 29, 1, 0), start_cd=2)
        self.add_moves(Move("Dragon Bone", 35, 4, 0), start_cd=4)
        self.add_moves(Move("Soul Split Katana Slash", 37, 5, 0), start_cd=4)

    def modify_incoming(self, attacker, _move, damage):
        # BALANCE/REWORK: Heavenly Restriction - no cursed energy to resist domains, so they hit 20% harder
        if attacker.domain_active:
            return int(damage * 1.2)
        return damage


class Megumi(Jjk):
    def __init__(self):
        super().__init__("Megumi Fushiguro", 157, 103,
                         "Round Dear is a healing move. Divine General Mahoraga can force stalemates. Be careful.",
                         "Potential Man")
        self.add_moves(Move("Divine Dogs", 18, 0, 12), start_cd=0)
        self.add_moves(Move("Toad", 24, 2, 13), start_cd=1)
        self.add_moves(Move("Max Elephant", 35, 3, 21), start_cd=2)
        self.add_moves(Move("Round Dear", -24, 2, 15), start_cd=0)
        self.add_moves(Move("Divine General MAHORAGA", 0, 10, 30), start_cd=10)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Chimera Shadow Garden", 0, 5, 50, is_domain=True), start_cd=5)


class Todo(Jjk):
    def __init__(self):
        super().__init__("Aoi Todo", 154, 95,
                         "Boogie Woogie has around a 41 percent chance to dodge. Use it before the opponent uses their trump card. Simple Domain nullifies a chunk of damage.",
                         "The Loyal Besto Friendo")
        self.add_moves(Move("Boogie Woogie", 13, 2, 20), start_cd=0)
        self.add_moves(Move("Black Flash", 35, 4, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Besto Friendo", 20, 1, 0), start_cd=1)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Takada + Besto Friendo", 32, 2, 24), start_cd=3)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)


class Yuki(Jjk):
    def __init__(self):
        super().__init__("Yuki Tsukumo", 177, 124,
                         "Black Hole can force stalemates. Simple Domain nullifies a chunk of damage.",
                         "The Star Vessel")
        self.add_moves(Move("Garudo Attack", 25, 0, 15), start_cd=0)
        self.add_moves(Move("Mass Control", 29, 2, 20), start_cd=1)
        self.add_moves(Move("Black Hole", 0, 10, 20), start_cd=10)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 25), start_cd=1)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Celestial Star Forge", 0, 5, 50, is_domain=True), start_cd=5)


class Yuta(Jjk):
    def __init__(self):
        super().__init__("Yuta Okkotsu", 168, 146,
                         "'Call to Rika' gives the user access to more copied techniques that can be used. Inside it, Hollow Purple and Black Flash have a 10 percent chance of doing double damage.",
                         "The Prodigy")
        self.add_moves(Move("CE Reserve", 20, 0, 20), start_cd=0)
        self.add_moves(Move("Slash", 23, 2, 20), start_cd=1)
        self.add_moves(Move("Rika", 32, 4, 40), start_cd=2)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd=1)
        self.add_moves(Move("Call to Rika", 0, 5, 35), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Authentic Mutual Love", 0, 5, 50, is_domain=True), start_cd=5)


class Nanami(Jjk):
    def __init__(self):
        super().__init__("Kento Nanami", 115, 110,
                         "Has a bigger chance to hit a critical. When under half of max hp he hits overtime, dealing +5 damage and taking 10 percent less damage. Black Flash can hit a double critical, 'Ratio Technique' and 'Collapsed Strike' have their own criticals.",
                         "The Workaholic")
        self.add_moves(Move("Ratio Technique", 26, 0, 15, crit=1.53), start_cd=0)
        self.add_moves(Move("Collapsed Strike", 34, 2, 25, crit=1.6), start_cd=2)
        self.add_moves(Move("Black Flash", 35, 3, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)

    def modify_incoming(self, _attacker, _move, damage):
        # BALANCE/REWORK: in Overtime he stays on the clock and takes 10% less damage
        if self.overtime:
            return int(damage * 0.9)
        return damage


class Sukuna(Jjk):
    def __init__(self):
        super().__init__("Ryomen Sukuna", 163, 151,
                         "Fuga has a random burning effect. Black Flash has a 10 percent chance of doing double damage.",
                         "The King of Curses")
        self.add_moves(Move("Slash", 20, 0, 20), start_cd=0)
        self.add_moves(Move("Dismantle", 30, 3, 23), start_cd=2)
        self.add_moves(Move("Fuga", 36, 4, 35, burn=True), start_cd=2)
        self.add_moves(Move("Black Flash", 35, 4, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("World Cutting Slash", 100, 11, 150, soul_resistence=True), start_cd=11)
        self.add_moves(Move("Malevolent Shrine", 0, 5, 50, is_domain=True), start_cd=5)


class Toji(Jjk):
    def __init__(self):
        super().__init__("Toji Fushiguro", 120, 0,
                         "Toji becomes stronger when the opponent opens their domain, but domains hit him 20 percent harder. Inverted Spear of Heaven can not be dodged.",
                         "No Cursed Energy Monster")
        self.add_moves(Move("Punch", 19, 0, 0), start_cd=0)
        self.add_moves(Move("Sword Slash", 29, 1, 0), start_cd=2)
        self.add_moves(Move("Chain of a Thousand Miles", 34, 4, 0), start_cd=4)
        self.add_moves(Move("Inverted Spear Of Heaven", 42, 5, 0), start_cd=4)

    def modify_incoming(self, attacker, _move, damage):
        # BALANCE/REWORK: Heavenly Restriction - no cursed energy to resist domains, so they hit 20% harder
        if attacker.domain_active:
            return int(damage * 1.2)
        return damage


class Kenjaku(Jjk):
    def __init__(self):
        super().__init__("Kenjaku", 162, 115,
                         "Kenjaku has a chance to receive less damage when the attack is too strong.",
                         "The Immortal")
        self.add_moves(Move("Cursed Spirit Manipulation", 20, 0, 15), start_cd=0)
        self.add_moves(Move("Maximum: Uzumaki", 39, 4, 25), start_cd=2)
        self.add_moves(Move("Antigravity System", 27, 3, 20), start_cd=1)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Womb Profusion", 0, 5, 50, is_domain=True), start_cd=5)


class Mahito(Jjk):
    def __init__(self):
        super().__init__("Mahito", 172, 103,
                         "Black Flash can hit a double damage critical. Mahito receives less damage for MOST attacks.",
                         "The Soul Shaper", soul_attack=True)
        self.add_moves(Move("Idle Transfiguration", 35, 3, 25), start_cd=1)
        self.add_moves(Move("Black Flash", 35, 3, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Morphing Punch", 12, 0, 15), start_cd=0)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Self-Embodiment of Perfection", 0, 5, 50, is_domain=True), start_cd=5)


class Jogo(Jjk):
    def __init__(self):
        super().__init__("Jogo", 142, 106,
                         "His first 3 attacks have a random burning effect.",
                         "The Volcano")
        self.add_moves(Move("Disaster Flames", 20, 0, 15, burn=True), start_cd=0)
        self.add_moves(Move("Ember Insects", 30, 2, 23, burn=True), start_cd=2)
        self.add_moves(Move("Maximum: Meteor", 35, 3, 27, burn=True), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Coffin of The Iron Mountain", 0, 5, 50, is_domain=True), start_cd=5)


class Uraume(Jjk):
    def __init__(self):
        super().__init__("Uraume", 140, 103,
                         "Her 'Frost Barrage' attack has a random chance of freezing her opponent for one turn. Every hit chills the enemy (max 4): chilled fighters deal 4 percent less damage per stack, and Frost Barrage freezes more often.",
                         "The Ice Queen")
        self.add_moves(Move("Icefall", 22, 0, 15), start_cd=0)
        self.add_moves(Move("Frost Calm", 32, 2, 22), start_cd=1)
        self.add_moves(Move("Frost Barrage", 27, 3, 30, freeze=True), start_cd=2)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 25), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)

    def on_hit(self, enemy, move):
        # BALANCE/REWORK: every hit chills the enemy (max 4 stacks). Chilled fighters deal 4% less
        # damage per stack, and Frost Barrage gets +6% freeze chance per stack.
        if move.damage <= 0:
            return
        enemy.chill = min(4, enemy.chill + 1)
        out(f"\n{enemy.name} is chilled! (Chill x{enemy.chill})")
        if move.name == "Frost Barrage" and random.randint(1, 100) <= enemy.chill * 6:
            enemy.frozen = True
            out(f"{enemy.name} was flash-frozen by the cold!")


class Naoya(Jjk):
    def __init__(self):
        super().__init__("Naoya Zenin", 152, 109,
                         "By using 'Projection Sorcery' the user can get 'faster' and do more damage that stacks with 'Mach 3 Tackle.' Frame Freeze has a chance of freezing the opponent for one turn.",
                         "The Fastest")
        self.add_moves(Move("Projection Sorcery", 0, 2, 18), start_cd=0)
        self.add_moves(Move("Frame Blitz", 24, 0, 15), start_cd=0)
        self.add_moves(Move("Mach 3 Tackle", 42, 4, 35), start_cd=2)
        self.add_moves(Move("Frame Freeze", 18, 3, 25, freeze=True), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Time Cell Moon Palace", 0, 5, 50, is_domain=True), start_cd=5)


class Hakari(Jjk):
    STATUS = {**Jjk.STATUS, "jackpot": ("JACKPOT", "yellow")}

    def __init__(self):
        super().__init__("Kinji Hakari", 166, 100,
                         "Idle Death Gamble has a 35 percent chance to hit the JACKPOT: for the whole domain he "
                         "heals 10 HP and regains 20 CE every turn and deals +8 damage. Pachinko Barrage is a gamble: "
                         "its damage can be halved or doubled.",
                         "The Gambler")
        self.jackpot = False
        self.add_moves(Move("Rough Energy", 22, 0, 10), start_cd=0)
        self.add_moves(Move("Shutter Doors Slam", 28, 2, 18), start_cd=1)
        self.add_moves(Move("Pachinko Barrage", 30, 3, 25), start_cd=2)
        self.add_moves(Move("Reverse Cursed Technique", -18, 3, 22), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Idle Death Gamble", 0, 5, 50, is_domain=True), start_cd=5)

    def activate_domain(self, domain_name, turns):
        super().activate_domain(domain_name, turns)
        if domain_name == "Idle Death Gamble":
            if random.randint(1, 100) <= 35:
                self.jackpot = True
                say("\n7... 7... 7... JACKPOT! Hakari's cursed energy overflows!")
            else:
                self.jackpot = False
                say("\nThe reels stop... no jackpot this time.")

    def reduce_domain(self):
        super().reduce_domain()
        if not self.domain_active:
            self.jackpot = False

    def on_turn_tick(self, _enemy):
        if self.jackpot and self.domain_active:
            self.ce = min(self.max_ce, self.ce + 20)
            healed = self.gain_hp(10)
            say(f"\nThe jackpot rushes through {self.name}: +20 CE, healed {healed} HP")

    def _domain_idle_death_gamble(self, _enemy, damage):
        return damage + (8 if self.jackpot else 3)

    def modify_outgoing(self, _enemy, move, damage):
        if move.name == "Pachinko Barrage":
            multiplier = random.choice([0.5, 0.8, 1.0, 1.2, 1.5, 2.0])
            out(f"\nThe reels spin... x{multiplier}!")
            damage = int(damage * multiplier)
        return damage


class Inumaki(Jjk):
    STATUS = {**Jjk.STATUS, "strain": ("Strain", "red")}
    SPEECH = {"Stop!": 0, "Crush": 2, "Explode": 5}  # command -> self-damage

    def __init__(self):
        super().__init__("Toge Inumaki", 156, 100,
                         "Every command strains his throat: +3 damage per Strain stack on his next commands. At 4 "
                         "stacks his throat gives out and he takes 8 damage. Crush and Explode also cost him HP. Throat Spray heals and clears Strain. "
                         "'Stop!' cannot be dodged.",
                         "The Cursed Speech User")
        self.strain = 0
        self.add_moves(Move("Stop!", 14, 3, 15, freeze=True), start_cd=1)
        self.add_moves(Move("Crush", 32, 2, 22), start_cd=1)
        self.add_moves(Move("Explode", 46, 4, 30), start_cd=3)
        self.add_moves(Move("Throat Spray", -22, 3, 20), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)

    def modify_outgoing(self, enemy, move, damage):
        if move.name in self.SPEECH:
            damage += self.strain * 3
        return damage

    def on_hit(self, enemy, move):
        if move.name not in self.SPEECH:
            return
        self.strain += 1
        self.hp = max(1, self.hp - self.SPEECH[move.name])
        out(f"\n{self.name}'s throat strains... (Strain x{self.strain})")
        if self.strain >= 4:
            self.hp = max(1, self.hp - 8)
            self.strain = 0
            say(f"{self.name}'s throat gives out! He takes 8 damage. HP: {self.hp}")

    def heal(self, move):
        result = super().heal(move)
        self.strain = 0
        return result


class Higuruma(Jjk):
    STATUS = {**Jjk.STATUS, "verdict_given": ("Guilty verdict", "magenta")}

    def __init__(self):
        super().__init__("Hiromi Higuruma", 162, 105,
                         "Deadly Sentencing: on the first hit inside the domain Judgeman delivers a GUILTY verdict "
                         "and confiscates the enemy's strongest attack for 4 turns. The Executioner's Sword hits "
                         "+14 harder while the verdict stands.",
                         "The Lawyer")
        self.verdict_given = False
        self.add_moves(Move("Gavel Strike", 23, 0, 12), start_cd=0)
        self.add_moves(Move("Cross-Examination", 30, 2, 20), start_cd=1)
        self.add_moves(Move("Executioner's Sword", 36, 4, 32), start_cd=3)
        self.add_moves(Move("Reverse Cursed Technique", -20, 3, 25), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Deadly Sentencing", 0, 5, 50, is_domain=True), start_cd=5)

    def activate_domain(self, domain_name, turns):
        super().activate_domain(domain_name, turns)
        self.verdict_given = False

    def reduce_domain(self):
        super().reduce_domain()
        if not self.domain_active:
            self.verdict_given = False

    def _domain_deadly_sentencing(self, enemy, damage):
        if not self.verdict_given:
            self.verdict_given = True
            candidates = [m for m in enemy.moves if m.damage > 0 and not m.is_domain]
            if candidates:
                best = max(candidates, key=lambda m: m.damage)
                enemy.cooldown[best.name] = max(enemy.cooldown.get(best.name, 0), 4)
                say(f"\nGUILTY. Judgeman confiscates {enemy.name}'s {best.name}!")
        return damage + 6

    def modify_outgoing(self, _enemy, move, damage):
        if move.name == "Executioner's Sword" and self.verdict_given and self.domain_active:
            damage += 14
            out("\nThe Executioner's Sword answers the guilty verdict!")
        return damage


class Kashimo(Jjk):
    STATUS = {**Jjk.STATUS, "charge": ("Charge", "yellow")}

    def __init__(self):
        super().__init__("Hajime Kashimo", 133, 115,
                         "Gains 1 Charge each turn (max 5). Each Charge adds +1 damage to every attack, but at 4+ "
                         "Charge the current burns him for 3 HP a turn. Mythical Beast Amber spends all Charge for "
                         "+5 damage each. Discharge can paralyze.",
                         "The God of Lightning")
        self.charge = 0
        self.add_moves(Move("Lightning Palm", 22, 0, 12), start_cd=0)
        self.add_moves(Move("Thunder Strike", 30, 2, 20), start_cd=1)
        self.add_moves(Move("Discharge", 24, 3, 25, freeze=True), start_cd=2)
        self.add_moves(Move("Mythical Beast Amber", 52, 7, 55), start_cd=5)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)

    def on_turn_tick(self, enemy):
        self.charge = min(5, self.charge + 1)
        out(f"\n{self.name} crackles with lightning. (Charge x{self.charge})")
        if self.charge >= 4:
            self.hp = max(1, self.hp - 3)
            out(f"The current burns {self.name} for 3 HP. HP: {self.hp}")

    def modify_outgoing(self, enemy, move, damage):
        damage += self.charge
        if move.name == "Mythical Beast Amber":
            damage += self.charge * 5
            out(f"\n{self.name} unleashes all {self.charge} Charge!")
            self.charge = 0
        return damage

    def _ai_value(self, move, enemy):
        if move.name == "Mythical Beast Amber":
            return move.damage + self.charge * 6
        return move.damage


class MeiMei(Jjk):
    STATUS = {**Jjk.STATUS, "crows": ("Crows", "white")}

    def __init__(self):
        super().__init__("Mei Mei", 142, 110,
                         "Summon Crows gives her up to 4 crows. Each crow pecks the enemy for 5 damage at the start of "
                         "her turn (cannot be dodged). Crow Barrage sacrifices all crows for +12 damage each. "
                         "Summon Crows cannot be dodged.",
                         "The Crow Mercenary")
        self.crows = 0
        self.add_moves(Move("Axe Slash", 22, 0, 12), start_cd=0)
        self.add_moves(Move("Bird Strike", 34, 3, 30), start_cd=2)
        self.add_moves(Move("Summon Crows", 0, 2, 15), start_cd=0)
        self.add_moves(Move("Crow Barrage", 20, 3, 25), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)

    def on_turn_tick(self, enemy):
        if self.crows > 0:
            damage = self.crows * 5
            enemy.hp = max(0, enemy.hp - damage)
            say(f"\n{self.name}'s {self.crows} crows peck {enemy.name} for {damage} damage. "
                f"{enemy.name} is at {enemy.hp} hp")

    def on_hit(self, _enemy, move):
        if move.name == "Summon Crows":
            self.crows = min(4, self.crows + 2)
            out(f"\n{self.name} calls her crows! (Crows x{self.crows})")

    def modify_outgoing(self, enemy, move, damage):
        if move.name == "Crow Barrage" and self.crows:
            damage += self.crows * 12
            out(f"\n{self.crows} crows dive in a sacrificial barrage!")
            self.crows = 0
        return damage

    def _ai_value(self, move, _enemy):
        if move.name == "Summon Crows":
            return 28 if self.crows < 2 else 0
        if move.name == "Crow Barrage":
            return move.damage + self.crows * 12 if self.crows >= 2 else 0
        return move.damage


NEW_ROSTER = [Hakari, Inumaki, Higuruma, Kashimo, MeiMei]