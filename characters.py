from moves import Move
from utilities import safe_int_input
import random
import time
PAUSE = 1.2
 
DOMAIN_MOVES = [
    "Malevolent Shrine", "Unlimited Void", "Chimera Shadow Garden",
    "Celestial Star Forge", "Authentic Mutual Love", "Womb Profusion",
    "Self-Embodiment of Perfection", "Coffin of The Iron Mountain",
    "Benevolent Shrine", "Time Cell Moon Palace",
]
# Every domain except Benevolent Shrine is a guaranteed hit
CANNOT_DODGE_DOMAINS = [d for d in DOMAIN_MOVES if d != "Benevolent Shrine"]
UNDODGEABLE_MOVES = {"Inverted Spear Of Heaven", "Soul Split Katana Slash"}
 
# (low, high) of a 0-100 roll that counts as a dodge
DEFAULT_DODGE = (52, 58)
DODGE_RANGES = {
    "Toji Fushiguro": (45, 65),
    "Maki Zenin": (47, 63),
    "Satoru Gojo": (47, 63),
}
 
# Yuta's domain: technique 
YUTA_TECHNIQUES = {
    "Limitless": (6, 4),
    "Dismantle": (6, 4),
    "Ice Breaker": (4, 6),
    "Cursed Speech": (4, 6),
    "Jacob's Ladder": (2, 9),
}
 
# Domain name 
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
 
 
def say(text):
    time.sleep(PAUSE)
    print(text)
 
 
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
 
        Jjk.number += 1
 
    def __str__(self):
        return self.name
 
    def is_alive(self):
        return self.hp > 0
 
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
        print(f"{self.name} HP: {self.hp} | CE: {self.ce}/{self.max_ce}")
        for i, move in enumerate(self.moves, 1):
            time.sleep(PAUSE)
            print(f"{i}. {move.name} |Damage: {move.damage}| CE cost: {move.ce_cost} "
                  f"| Cooldown: {self.cooldown[move.name]}")
 
    def on_cooldown(self, move):
        if self.cooldown[move.name] > 0:
            print(f"\n{move.name} is on cooldown! Choose another move. ")
            return True
        return False
 
    def _finish_move(self, move):
        """Pay the CE cost and start the cooldown for a move that was used."""
        self.spend_ce(move.ce_cost)
        self.cooldown[move.name] = move.cooldown

    def focus_ce(self):
        gain = random.randint(20, 35)
        self.ce = min(self.ce + gain, self.max_ce)
        print(f"\n{self.name} focused and regained {gain} CE")
 
    def regain_ce(self):
        regain = random.randint(2, 8)
        self.ce = min(self.ce + regain, self.max_ce)
        say(f"\n{self.name} regained {regain} CE")
 
    def reduce_cooldown(self):
        for move_name in self.cooldown:
            if self.cooldown[move_name] > 0:
                self.cooldown[move_name] -= 1
 
    def apply_status_effect(self, enemy):
        if enemy.is_alive() and self.burn_turns > 0:
            say(f"\n{self.name} is burning")
            self.hp = max(0, self.hp - self.burn_damage)
            say(f"{self.name} took {self.burn_damage} burn damage")
            print(f"{self.name} is at {self.hp} HP")
            self.burn_turns -= 1
 
    def activate_domain(self, domain_name, turns):
        self.domain_active = True
        self.domain_turns = turns
        self.domain_name = domain_name
        print(f"\n{self.name} opened their domain: ")
        say(domain_name)
 
    def reduce_domain(self):
        if self.domain_active:
            self.domain_turns -= 1
            if self.domain_turns <= 0:
                print(f"\n{self.domain_name} faded away...")
                self.domain_active = False
                self.domain_name = ""
 
    def activate_simple_domain(self, turns):
        self.simple_domain = True
        self.simple_domain_turns = turns
        print(f"\n{self.name} activated New Shadow Style Technique: Simple Domain")
        say(f"{self.name} neutralizes techniques around them.")
 
    def reduce_simple_domain(self):
        if self.simple_domain:
            self.simple_domain_turns -= 1
            if self.simple_domain_turns <= 0:
                print(f"{self.name}'s simple domain shattered")
                self.simple_domain = False
 
    def _yuta_technique_bonus(self, message, index):
        print(message)
        choice = random.choice(list(YUTA_TECHNIQUES))
        print(choice)
        return YUTA_TECHNIQUES[choice][index]
 
    def heal(self, move):
        amount = max(0, random.randint(-move.damage - 5, -move.damage + 5))
        print(f"\n{self.name} used {move.name}")
        if self.domain_name == "Authentic Mutual Love":
            amount += 4 + self._yuta_technique_bonus(
                f"\n{self.name} gets healed by one of these techniques: ", 1)
        healed = self.gain_hp(amount)
        say(f"\n{self.name} healed {healed} hp")
        say(f"{self.name} is at {self.hp} hp")
        self._finish_move(move)
        return True
 
    def suicide_move(self, enemy, move):
        enemy.hp = 0
        self.hp = 0
        print(f"\n{self.name} used {move.name}")
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
        print("\nChoose a move:")
        for i, move in enumerate(options, 1):
            print(f"{i}. {move.name} | Damage: {move.damage}")
            time.sleep(PAUSE)
        while True:
            choice = safe_int_input("Choose the move: ")
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print("Invalid move.")
 
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
        """Roll the enemy's dodge. Returns a message if they dodged, else None."""
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
        """Returns True if the attack was dodged (the move is still spent)."""
        message = self._dodge_message(enemy, move)
        if message is None:
            return False
        print(f"\n{self.name} used {move.name}")
        say(message)
        self._finish_move(move)
        return True

    def _domain_malevolent_shrine(self, enemy, damage):
        print(f"\n{enemy.name} gets cleaved and dismantled by the Shrine")
        return int(damage * 1.225)
 
    def _domain_chimera_shadow_garden(self, enemy, damage):
        print(f"\n{enemy.name} gets lost in the shadows and got attacked by some clones")
        return int(damage * 1.225) + random.randint(4, 10)
 
    def _domain_authentic_mutual_love(self, enemy, damage):
        bonus = self._yuta_technique_bonus(
            f"\n{enemy.name} gets hit by one of these techniques: ", 0)
        return damage + 4 + bonus
 
    def _domain_celestial_star_forge(self, enemy, damage):
        print(f"\n{enemy.name} gets crushed under the Star")
        self.hp = max(0, self.hp - 4)
        print(f"\n{self.name} gets damaged from her innate technique inside the domain, health: {self.hp}")
        return int(damage * 1.2) + 7
 
    def _domain_womb_profusion(self, enemy, damage):
        print(f"\n{self.name} creates a tree of grotesque human faces...")
        return damage + 12
 
    def _domain_self_embodiment(self, enemy, damage):
        print(f"\n{self.name} shows the embodiment of his Perfection...")
        self.gain_hp(random.randint(7, 15))
        print(f"{self.name} heals himself within the domain...\n{self.name} is at {self.hp} hp")
        return damage + 10
 
    def _domain_coffin(self, enemy, damage):
        print("\nA Large Mountain spews lava. It is getting extremely hot")
        return max(int(damage * 1.5) - 6, 0)
 
    def _domain_benevolent_shrine(self, enemy, damage):
        print("\nHappy memories flood the domain.")
        self.gain_hp(12)
        print(f"{self.name} heals his soul from the domain, {self.hp} hp")
        return max(int(damage * 1.65 - 9), 0)
 
    def _domain_time_cell(self, enemy, damage):
        print(f"\n{enemy.name}'s cells are forced into frames!")
        if random.randint(1, 100) <= 45:
            enemy.frozen = True
            print(f"{enemy.name} failed to follow the 24 FPS rule and froze!")
        return damage + self.speed_stack * 5
 

    def _check_overtime(self):
        if self.name == "Kento Nanami" and not self.overtime and self.hp <= self.max_hp // 2:
            self.overtime = True
            say("\nNanami entered Overtime...")
 
    def _roll_damage(self, move):
        """Base damage with variance. Returns (damage, was_critical)."""
        low_roll = 1 if self.name == "Kento Nanami" else 0  # Nanami crits more often
        is_crit = random.randint(low_roll, 10) == 10
        damage = max(0, random.randint(move.damage - 3, move.damage + 3))
        if is_crit:
            damage = int(damage * move.crit)
        return damage, is_crit
 
    def _apply_on_hit_effects(self, enemy, move):
        """Side effects that happen whenever a move lands."""
        if move.name == "Projection Sorcery":
            self.projection_active = True
            self.speed_stack += 1
            print(f"{self.name} accelerated with Projection sorcery!")
 
        if move.freeze and random.randint(0, 100) <= 45:
            enemy.frozen = True
 
        if self.name == "Choso Kamo" and move.blood:
            enemy.blood_stack += 1
            print(f"\n{enemy.name} gained a Blood Stack!")
            print(f"Blood Stacks: {enemy.blood_stack}")
 
        if move.name == "Boogie Woogie":
            self.boogie_woogie_dodge = True
            say(f"\n{self.name} becomes unpredictable with {move.name}")
 
        if move.burn and random.randint(1, 100) <= 39:
            enemy.burn_turns = 2
            enemy.burn_damage = 8
            print(f"\n{enemy.name} was burned!")
 
    def _apply_attacker_bonuses(self, enemy, move, damage):
        if self.name == "Toji Fushiguro" and enemy.domain_active:
            damage += 15
            print("Toji Fushiguro gets mildly affected by the domain.")
 
        if self.name == "Maki Zenin" and self.hp <= self.max_hp / 2:
            damage += 10
            print("Maki Zenin enters a rage mode.")
 
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
                print("\nNanami struck the 7:3 weak point!")
                damage += 5
 
        return damage
 
    def _apply_defender_reductions(self, enemy, move, damage):
        if enemy.domain_name == "Unlimited Void":
            damage = max(damage // 2, 0)
            print(f"{self.name} is stunned with infinite knowledge")
 
        if enemy.domain_name == "Chimera Shadow Garden":
            damage = max(damage // 3, 0)
            print(f"\nShadows are taking over {self.name}")
 
        if enemy.simple_domain:
            if self.domain_active:
                print(f"\n{enemy.name}'s Simple Domain disrupts the guaranteed-hit effect!")
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
 
        return damage
 
    def _deal_damage(self, enemy, damage):
        enemy.hp = max(0, enemy.hp - damage)
        say(f"{enemy.name} took {damage} damage")
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
            print(f"\n{self.name} entered the zone and hit a critical {move.name}")
        else:
            print(f"\n{self.name} used {move.name}")
 
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
            print(f"\nNot enough Cursed Energy for {move.name}")
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
 
    def choose_move(self, enemy):
        if self.name not in ("Toji Fushiguro", "Maki Zenin") and self.ce <= 15:
            return "focus"
 
        available = [
            (i, move) for i, move in enumerate(self.moves)
            if self.cooldown[move.name] == 0 and self.ce >= move.ce_cost
        ]
        if not available:
            return "focus"
 
        def strongest():
            return max(available, key=lambda pair: pair[1].damage)[0]
 
        if self.hp <= 25:
            if enemy.hp < 30:
                return strongest()  # go for the kill
            heals = [pair for pair in available if pair[1].damage < 0]
            if heals:
                return random.choice(heals)[0]
 
        for i, move in available:
            if move.name in DOMAIN_MOVES and enemy.hp <= 70 and self.hp <= 60:
                return i
 
        if random.randint(1, 100) <= 25:  # not always the strongest move
            return random.choice(available)[0]
        return strongest()
 
 

class Yuji(Jjk):
    def __init__(self):
        super().__init__("Yuji Itadori", 162, 103,
                         "Black Flashes have a 10 percent chance to do double damage. Simple Domain nullifies a chunk of damage.",
                         "The Strongest of The Future")
        self.add_moves(Move("Divergent Fist", 17, 0, 10, soul_resistence=True), start_cd=0)
        self.add_moves(Move("Black Flash", 35, 2, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Cleave and Dismantle", 22, 1, 20), start_cd=2)
        self.add_moves(Move("Blood Manipulation", 25, 3, 20), start_cd=2)
        self.add_moves(Move("Reverse Cursed Technique", -20, 3, 20), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Benevolent Shrine", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Gojo(Jjk):
    def __init__(self):
        super().__init__("Satoru Gojo", 144, 140,
                         "Gojo has a 17 percent chance of dodging. Hollow Purple and Black Flash has a 10 percent chance to do double the damage. Simple Domain nullifies a chunk of damage.",
                         "The Honored One")
        self.add_moves(Move("Blue", 20, 0, 15, soul_resistence=True), start_cd=0)
        self.add_moves(Move("Red", 30, 2, 25, soul_resistence=True), start_cd=1)
        self.add_moves(Move("Hollow Purple", 40, 3, 45, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Reverse Cursed Technique", -20, 3, 25), start_cd=1)
        self.add_moves(Move("Black Flash", 35, 3, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Unlimited Void", 0, 5, 35, is_domain=True), start_cd=5)
 
 
class Choso(Jjk):
    def __init__(self):
        super().__init__("Choso Kamo", 150, 93,
                         "Save his blood stacks for supernova as the blood stacks can EXPLODE with Supernova dealing extra burst damage.",
                         "The Blood Brother")
        self.add_moves(Move("Convergence", 20, 0, 15, blood=True), start_cd=0)
        self.add_moves(Move("Piercing Blood", 23, 2, 17, blood=True), start_cd=2)
        self.add_moves(Move("Supernova", 20, 3, 20), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Slicing Exorcism", 31, 3, 21, blood=True), start_cd=3)
 
 
class Maki(Jjk):
    def __init__(self):
        super().__init__("Maki Zenin", 172, 0,
                         "Soul Split Katana Slash cannot be dodged. She has extra damage when in low health.",
                         "Zero Cursed Energy Empress")
        self.add_moves(Move("Polearms hit", 20, 0, 0), start_cd=0)
        self.add_moves(Move("Mai's Wrath", 30, 1, 0), start_cd=2)
        self.add_moves(Move("Dragon Bone", 33, 3, 0), start_cd = 4)
        self.add_moves(Move("Soul Split Katana Slash", 40, 4, 0), start_cd=4)
 
 
class Megumi(Jjk):
    def __init__(self):
        super().__init__("Megumi Fushiguro", 150, 103,
                         "Divine General Mahoraga can force stalemates. Be careful.",
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
        super().__init__("Aoi Todo", 168, 95,
                         "Boogie Woogie has around a 20 percent chance to dodge. Use it before the opponent uses their trump card. Simple Domain nullifies a chunk of damage.",
                         "The Loyal Besto Friendo")
        self.add_moves(Move("Boogie Woogie", 13, 2, 20), start_cd=0)
        self.add_moves(Move("Black Flash", 35, 4, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Besto Friendo", 20, 1, 0), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Takada + Besto Friendo", 32, 2, 24), start_cd=3)
 
 
class Yuki(Jjk):
    def __init__(self):
        super().__init__("Yuki Tsukumo", 162, 124,
                         "Black Hole can force stalemates. Simple Domain nullifies a chunk of damage.",
                         "The Star Vessel")
        self.add_moves(Move("Garudo Attack", 23, 0, 15), start_cd=0)
        self.add_moves(Move("Mass Control", 27, 2, 20), start_cd=1)
        self.add_moves(Move("Black Hole", 0, 10, 20), start_cd=10)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 25), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd=2)
        self.add_moves(Move("Celestial Star Forge", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Yuta(Jjk):
    def __init__(self):
        super().__init__("Yuta Okkotsu", 144, 146,
                         "'Call to Rika' gives the user access to more copied techniques that can be used. Inside it, Hollow Purple and Black Flash have a 10 percent chance of doing double damage.",
                         "The Prodigy")
        self.add_moves(Move("CE Reserve", 20, 0, 20), start_cd=0)
        self.add_moves(Move("Slash", 23, 2, 25), start_cd=1)
        self.add_moves(Move("Rika", 32, 4, 40), start_cd=2)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd=1)
        self.add_moves(Move("Call to Rika", 0, 5, 40), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Authentic Mutual Love", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Nanami(Jjk):
    def __init__(self):
        super().__init__("Kento Nanami", 115, 110,
                         "Has a bigger chance to hit a critical. When under half of max hp he hits overtime. Black Flash can hit a double critical, 'Ratio Technique' and 'Collapsed Strike' have their own criticals.",
                         "The Workaholic")
        self.add_moves(Move("Ratio Technique", 26, 0, 15, crit=1.53), start_cd=0)
        self.add_moves(Move("Collapsed Strike", 34, 2, 25, crit=1.6), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Black Flash", 35, 3, 25, crit=2, soul_resistence=True), start_cd=3)
 
 
class Sukuna(Jjk):
    def __init__(self):
        super().__init__("Ryomen Sukuna", 180, 151,
                         "Fuga has a random burning effect. Black Flash has a 10 percent chance of doing double damage.",
                         "The King of Curses")
        self.add_moves(Move("Slash", 20, 0, 20), start_cd=0)
        self.add_moves(Move("Dismantle", 30, 3, 23), start_cd=2)
        self.add_moves(Move("Fuga", 36, 4, 35, burn=True), start_cd=2)
        self.add_moves(Move("Black Flash", 35, 4, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd=1)
        self.add_moves(Move("World Cutting Slash", 100, 11, 150, soul_resistence=True), start_cd=11)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Malevolent Shrine", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Toji(Jjk):
    def __init__(self):
        super().__init__("Toji Fushiguro", 174, 0,
                         "Toji becomes stronger when the opponent opens their domain. Inverted Spear of Heaven can not be dodged.",
                         "No Cursed Energy Monster")
        self.add_moves(Move("Punch", 20, 0, 0), start_cd=0)
        self.add_moves(Move("Sword Slash", 30, 1, 0), start_cd=2)
        self.add_moves(Move("Chain of a Thousand Miles", 33, 3, 0), start_cd = 4)
        self.add_moves(Move("Inverted Spear Of Heaven", 40, 4, 0), start_cd=4)
 
 
class Kenjaku(Jjk):
    def __init__(self):
        super().__init__("Kenjaku", 149, 115,
                         "Kenjaku has a chance to receive less damage when under a certain amount of HP.",
                         "The Immortal")
        self.add_moves(Move("Cursed Spirit Manipulation", 20, 0, 15), start_cd=0)
        self.add_moves(Move("Maximum: Uzumaki", 39, 4, 25), start_cd=2)
        self.add_moves(Move("Antigravity System", 27, 3, 20), start_cd=1)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Womb Profusion", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Mahito(Jjk):
    def __init__(self):
        super().__init__("Mahito", 144, 103,
                         "Black Flash can hit a double damage critical. Mahito receives less damage for MOST attacks.",
                         "The Soul Shaper", soul_attack=True)
        self.add_moves(Move("Idle Transfiguration", 33, 3, 25), start_cd=1)
        self.add_moves(Move("Black Flash", 35, 3, 25, crit=2, soul_resistence=True), start_cd=3)
        self.add_moves(Move("Morphing Punch", 12, 0, 15), start_cd=0)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Self-Embodiment of Perfection", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Jogo(Jjk):
    def __init__(self):
        super().__init__("Jogo", 162, 106,
                         "His first 3 attacks have a random burning effect.",
                         "The Volcano")
        self.add_moves(Move("Disaster Flames", 20, 0, 15, burn=True), start_cd=0)
        self.add_moves(Move("Ember Insects", 30, 2, 23, burn=True), start_cd=2)
        self.add_moves(Move("Maximum: Meteor", 35, 3, 27, burn=True), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Coffin of The Iron Mountain", 0, 5, 50, is_domain=True), start_cd=5)
 
 
class Uraume(Jjk):
    def __init__(self):
        super().__init__("Uraume", 156, 103,
                         "Her 'Frost Barrage' attack has a random chance of freezing her opponent for one turn.",
                         "The Ice Queen")
        self.add_moves(Move("Icefall", 22, 0, 15), start_cd=0)
        self.add_moves(Move("Frost Calm", 32, 2, 22), start_cd=1)
        self.add_moves(Move("Frost Barrage", 27, 3, 30, freeze=True), start_cd=2)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Reverse Cursed Technique", -20, 2, 25), start_cd=1)
 
 
class Naoya(Jjk):
    def __init__(self):
        super().__init__("Naoya Zenin", 142, 109,
                         "By using 'Projection Sorcery' the user can get 'faster' and do more damage that stacks with 'Mach 3 Tackle.' Frame Freeze has a chance of freezing the opponent for one turn.",
                         "The Fastest")
        self.add_moves(Move("Projection Sorcery", 0, 2, 18), start_cd=0)
        self.add_moves(Move("Frame Blitz", 24, 0, 15), start_cd=0)
        self.add_moves(Move("Mach 3 Tackle", 42, 4, 35), start_cd=2)
        self.add_moves(Move("Frame Freeze", 18, 3, 25, freeze=True), start_cd=1)
        self.add_moves(Move("Focus", 0, 0, 0), start_cd=0)
        self.add_moves(Move("Time Cell Moon Palace", 0, 5, 50, is_domain=True), start_cd=5)
 