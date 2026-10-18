#One-line descriptions for every move, shown on stat cards and in the battle menu.

#Text can use {damage}, {heal}, {cooldown} and {ce}; they are filled in from the move itself, so they stay correct when you rebalance a move in characters.py.

#Numbers that are NOT on the move (45% freeze chance, +6 per Blood Stack, domain multipliers...) live in characters.py

#To describe the same move name differently for one fighter, add it to OVERRIDES as (fighter name, move name): "text".

DESCRIPTIONS = {
    # ---- shared moves ----
    "Focus": "Skip your attack to regain 20-35 CE. No cost, no cooldown.",
    "Reverse Cursed Technique": "Heals about {heal} HP.",
    "Simple Domain": "Shields you for the next 2 enemy turns: their attacks deal 35% less damage (50% less if the attacker has a domain open).",
    "Black Flash": "Cursed energy lands within a split second of impact. About a 1 in 10 chance to crit for double damage.",
    "Slash": "A clean sword slash.",

    # ---- Yuji ----
    "Divergent Fist": "A fast, cheap strike with a delayed second impact.",
    "Cleave and Dismantle": "Borrowed Sukuna slashes. Solid damage on a short cooldown.",
    "Blood Manipulation": "Hits with controlled blood for decent damage.",
    "Benevolent Shrine": "Domain, lasts 4 turns. Each attack that lands heals you 12 HP. Damage is multiplied by 1.65, then reduced by 9.",

    # ---- Gojo ----
    "Blue": "Attractive force that crushes the target. Cheap and reliable.",
    "Red": "Repulsive force blast. Hard-hitting for the cost.",
    "Hollow Purple": "Fuses Blue and Red for massive damage. About a 1 in 10 chance to crit for double.",
    "Unlimited Void": "Domain, lasts 4 turns. The enemy's attacks deal half damage while it lasts. It does not boost your own damage.",

    # ---- Choso ----
    "Convergence": "Piercing blood shot. Adds a Blood Stack to the enemy.",
    "Piercing Blood": "A high-speed blood beam. Adds a Blood Stack to the enemy.",
    "Supernova": "Detonates every Blood Stack on the enemy for +6 damage each, then clears them.",
    "Slicing Exorcism": "A heavy blood slash. Adds a Blood Stack to the enemy.",

    # ---- Maki ----
    "Polearms hit": "Basic strikes with a cursed tool. No CE needed.",
    "Mai's Wrath": "A fierce combo built on Mai's memory. No CE needed.",
    "Dragon Bone": "A slashing combo with the cursed tool. No CE needed; long cooldown.",
    "Soul Split Katana Slash": "Cuts the soul directly. Cannot be dodged. No CE needed.",

    # ---- Megumi ----
    "Divine Dogs": "Summons the shikigami dogs for a quick attack.",
    "Toad": "The toad shikigami lashes out with its tongue.",
    "Max Elephant": "Floods the area with water for heavy damage.",
    "Round Dear": "Healing shikigami. Restores about {heal} HP.",
    "Divine General MAHORAGA": "Summons Mahoraga, who destroys the battlefield. Both fighters drop to 0 HP and the match ends in a draw.",
    "Chimera Shadow Garden": "Domain, lasts 4 turns. Your attacks deal x1.225 damage plus 4-10 from shadow clones, and the enemy's attacks deal only a third of their damage.",

    # ---- Todo ----
    "Boogie Woogie": "A light attack that primes a swap: each incoming attack has about a 41% chance to be dodged, until it triggers once.",
    "Besto Friendo": "A fast combo with his best friend. No CE needed.",
    "Takada + Besto Friendo": "Takada-chan's stage plus Besto Friendo. Strong and cheap with a short cooldown.",

    # ---- Yuki ----
    "Garudo Attack": "Garuda strikes from above. A cheap opener.",
    "Mass Control": "Manipulates mass to boost impact for solid damage.",
    "Black Hole": "Collapses the battlefield. Both fighters drop to 0 HP and the match ends in a draw.",
    "Celestial Star Forge": "Domain, lasts 4 turns. Your attacks deal x1.2 damage plus 7, but each attack costs you 4 HP.",

    # ---- Yuta ----
    "CE Reserve": "Burns through his huge reserve for a plain strike.",
    "Rika": "Rika attacks with raw cursed energy for a heavy hit.",
    "Call to Rika": "Choose one of Yuta's copied techniques: Cleave and Dismantle, Hollow Purple, Jacob's Ladder (heal), Cursed Speech or Black Flash. The technique costs no extra CE.",
    "Authentic Mutual Love": "Domain, lasts 4 turns. Each attack gains +6 to +10 damage from a random copied technique. Healing gains +8 to +13.",

    # ---- Nanami ----
    "Ratio Technique": "Targets the 7:3 weak point: 45% chance for +5 bonus damage.",
    "Collapsed Strike": "An overwhelming blow at the weak point: 45% chance for +5 bonus damage.",

    # ---- Sukuna ----
    "Dismantle": "Invisible slashes that cut everything. Strong and cheap.",
    "Fuga": "A flame arrow. 39% chance to burn the enemy for 8 damage a turn, for 2 turns.",
    "World Cutting Slash": "Cuts the world itself. Huge damage, very long cooldown, and it costs a lot of CE.",
    "Malevolent Shrine": "Domain, lasts 4 turns. Your attacks deal x1.225 damage.",

    # ---- Toji ----
    "Punch": "A brutal heavenly-restriction punch. No CE needed.",
    "Sword Slash": "A cursed tool slash. No CE needed.",
    "Chain of a Thousand Miles": "A cursed tool spun around in a wide area for heavy damage. No CE needed; long cooldown.",
    "Inverted Spear Of Heaven": "Cancels techniques. Cannot be dodged. No CE needed.",

    # ---- Kenjaku ----
    "Cursed Spirit Manipulation": "Throws absorbed curses at the target.",
    "Maximum: Uzumaki": "Releases a spiral of absorbed curses. His strongest regular attack.",
    "Antigravity System": "A gravity-defying strike for solid damage.",
    "Womb Profusion": "Domain, lasts 4 turns. Adds +12 damage to each of your attacks.",

    # ---- Mahito ----
    "Idle Transfiguration": "Reshapes the target's soul. Hits hard.",
    "Morphing Punch": "A quick, cheap shapeshifting blow.",
    "Self-Embodiment of Perfection": "Domain, lasts 4 turns. Each attack gets +10 damage and heals you 7-15 HP.",

    # ---- Jogo ----
    "Disaster Flames": "Basic flames. 39% chance to burn the enemy for 8 damage a turn, for 2 turns.",
    "Ember Insects": "A swarm of burning insects. 39% chance to burn the enemy for 8 damage a turn, for 2 turns.",
    "Maximum: Meteor": "Drops a meteor. 39% chance to burn the enemy for 8 damage a turn, for 2 turns.",
    "Coffin of The Iron Mountain": "Domain, lasts 4 turns. Scorching lava: damage is multiplied by 1.5, then reduced by 6.",

    # ---- Uraume ----
    "Icefall": "Ice crashes down on the target. Adds a Chill stack.",
    "Frost Calm": "A calm, precise freezing strike. Adds a Chill stack.",
    "Frost Barrage": "A storm of ice. About a 45% chance to freeze the enemy for a turn, higher with Chill. Adds a Chill stack.",

    # ---- Naoya ----
    "Projection Sorcery": "Gains a Speed stack: +5 damage on all your attacks per stack, and a better dodge chance.",
    "Frame Blitz": "A fast frame-by-frame strike.",
    "Mach 3 Tackle": "A devastating high-speed tackle. Your Speed stacks add to its damage.",
    "Frame Freeze": "Locks the enemy in a frame. About a 45% chance to freeze them for a turn.",
    "Time Cell Moon Palace": "Domain, lasts 4 turns. Each attack has a 45% chance to freeze the enemy and gains +5 damage per Speed stack. You also get about a 41% chance to dodge.",

    # ---- Hakari ----
    "Rough Energy": "A raw, cheap punch.",
    "Shutter Doors Slam": "Slams the target with his shutter-door technique.",
    "Pachinko Barrage": "A gamble: damage is multiplied by x0.5, x0.8, x1.0, x1.2, x1.5 or x2.0.",
    "Idle Death Gamble": "Domain, lasts 4 turns. 35% chance of JACKPOT: you heal 10 HP and regain 20 CE at the start of each of your turns, and attacks gain +8 damage (otherwise +3).",

    # ---- Inumaki ----
    "Stop!": "A command that cannot be dodged. About a 45% chance to freeze the enemy. Adds a Strain stack.",
    "Crush": "A crushing command. Costs you 2 HP and adds a Strain stack.",
    "Explode": "His strongest command. Costs you 5 HP and adds a Strain stack.",
    "Throat Spray": "Heals about {heal} HP and clears all Strain.",

    # ---- Higuruma ----
    "Gavel Strike": "A quick strike with the gavel.",
    "Cross-Examination": "A sharp, precise attack that pressures the target.",
    "Executioner's Sword": "Deals +14 damage while your guilty verdict stands (inside your domain).",
    "Deadly Sentencing": "Domain, lasts 4 turns. The first hit delivers a GUILTY verdict and confiscates the enemy's strongest attack for 4 turns. Every hit gets +6 damage.",

    # ---- Kashimo ----
    "Lightning Palm": "A lightning-charged palm strike.",
    "Thunder Strike": "A heavy bolt of lightning.",
    "Discharge": "Releases stored current. About a 45% chance to paralyze (freeze) the enemy.",
    "Mythical Beast Amber": "Spends all your Charge for +5 damage each. Huge damage and a very long cooldown.",

    # ---- Mei Mei ----
    "Axe Slash": "A swift slash with her axe.",
    "Bird Strike": "Crows dive in alongside her blade for heavy damage.",
    "Summon Crows": "Gains 2 crows (max 4). Cannot be dodged. Each crow pecks the enemy for 5 damage at the start of your turn.",
    "Crow Barrage": "Sacrifices all your crows for +12 damage each.",
}

# Same move name, different behavior for one fighter: (fighter name, move name) -> text
OVERRIDES = {
    ("Yuji Itadori", "Black Flash"): "Cursed energy lands within a split second of impact. About a 1 in 10 chance to crit for double damage. Each Black Flash that lands adds +4 damage to your next ones (max +12).",
}


def describe(move, fighter=None):
    """The text for a move. Pass the fighter to get any per-fighter wording."""
    text = None
    if fighter is not None:
        text = OVERRIDES.get((fighter.name, move.name))
    if text is None:
        text = DESCRIPTIONS.get(move.name)
    if text is None:
        text = _fallback(move)
    text = text.format(damage=move.damage, heal=-move.damage, cooldown=move.cooldown, ce=move.ce_cost)
    if getattr(move, "soul_resistence", False) and move.damage > 0:
        text += " Bypasses Mahito's soul resistance."
    return text


def _fallback(move):
    """Used only for a move nobody has written a description for yet."""
    if move.is_domain:
        return "Opens a domain for 4 turns."
    if move.damage < 0:
        return "Heals about {heal} HP."
    if move.damage == 0:
        return "A utility move."
    extras = []
    if getattr(move, "burn", False):
        extras.append("can burn")
    if getattr(move, "freeze", False):
        extras.append("can freeze")
    if getattr(move, "blood", False):
        extras.append("adds a Blood Stack")
    return "Deals about {damage} damage" + (", " + ", ".join(extras) if extras else "") + "."
