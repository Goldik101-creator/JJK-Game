from moves import Move
from utilities import safe_int_input
import random
import time
DOMAIN_MOVES =  ["Malevolent Shrine", "Unlimited Void", "Chimera Shadow Garden", "Celestial Star Forge", "Authentic Mutual Love", "Womb Profusion", "Self-Embodiment of Perfection", "Coffin of The Iron Mountain", "Benevolent Shrine", "Time Cell Moon Palace"]
CANNOT_DODGE_DOMAINS = ["Malevolent Shrine", "Unlimited Void", "Chimera Shadow Garden", "Celestial Star Forge", "Authentic Mutual Love", "Womb Profusion", "Self-Embodiment of Perfection", "Coffin of The Iron Mountain", "Time Cell Moon Palace"]
class Jjk: #creates the first class, the backbone basically
  number = 0
  def __init__(self, name, hp, ce, tip, title,soul_attack = False):
    self.name = name #the name of the character
    self.hp = hp #the hit points
    self.moves = [] #the list of moves
    self.cooldown = {} #the dictionary of moves inside because you can pick moves from them unlike sets which don't have place values
    self.domain_active = False
    self.domain_turns = 0
    self.domain_name = ""
    self.ce = ce
    self.max_ce = ce
    self.tip = tip
    self.title = title
    self.boogie_woogie_dodge = False
    self.burn_turns = 0
    self.burn_damage = 0
    self.blood_stack = 0
    self.frozen = False
    self.speed_stack = 0
    self.projection_active = False
    self.simple_domain = False
    self.simple_domain_turns = 0
    self.max_hp = hp
    self.soul_attack = soul_attack
    self.overtime = False
    self.ai = True
    Jjk.number += 1
  def __str__(self):
    return self.name #the name, returns the name

  def return_name_move(self, move_number): #returns what move comes
    return self.moves[move_number][0]
  def spend_ce(self, amount): #spends the cost of cursed energy
    self.ce = max(0, self.ce - amount)

  def add_moves(self, move, start_cd = 0): #adds like moves to teh character
    self.moves.append(move) #move name and the damage
    self.cooldown[move.name] = start_cd #the starting cooldown

  def show_moves(self): #shows the moves
    print(f"{self.name} HP: {self.hp} | CE: {self.ce}/{self.max_ce}")
    for i in range(len(self.moves)):
      move = self.moves[i] #stores the move
      time.sleep(0.7)
      print(f"{i+1}. {move.name} |Damage: {move.damage}| CE cost: {move.ce_cost} | Cooldown: {self.cooldown[move.name]}") #additional info about the move

  def return_num_moves(self): #returns the nuymber of moves
    return len(self.moves) - 1 #how many moves you have

  def on_cooldown(self, move): #checks if the move is on cooldown
    if self.cooldown[move.name] > 0: #if the cooldown is larger than 0, cant use the dam move
      print(f"\n{move.name} is on cooldown! Choose another move. ")
      return True
    else:
      return False
  def focus_ce(self): #makes the focus function to gain more CE
    gain = random.randint(20, 35)
    self.ce += gain
    self.ce = min(self.ce, self.max_ce)
    print(f"\n{self.name} focused and regained {gain} CE")

  def activate_simple_domain(self, turns): #activates the simple domain
    self.simple_domain = True
    self.simple_domain_turns = turns
    print(f"\n{self.name} activated New Shadow Style Technique: Simple Domain")
    time.sleep(0.7)
    print(f"{self.name} neutralizes techniques around them.")
  def reduce_simple_domain(self): #decreases the simple domian
    if self.simple_domain == True:
      self.simple_domain_turns -= 1
      if self.simple_domain_turns <= 0:
        print(f"{self.name}'s simple domain shattered")
        self.simple_domain = False

  def apply_status_effect(self, enemy): #applies the status effect
    if enemy.is_alive():
      if self.burn_turns > 0:
        time.sleep(0.7)
        print(f"\n{self.name} is burning")
        self.hp -= self.burn_damage
        self.hp = max(0, self.hp)
        time.sleep(0.7)
        print(f"{self.name} took {self.burn_damage} burn damage")
        print(f"{self.name} is at {self.hp} HP")
        self.burn_turns -= 1
  def heal(self, move): #healing
    heals = max(0, random.randint((-1* move.damage) - 5, (-1 * move.damage)+5)) #healing attacks
    if self.domain_name == "Authentic Mutual Love":
      heals += 4
      print(f"\n{self.name} gets healed by one of these techniques: ")
      yuta_choices = random.choice(["Limitless", "Jacob's Ladder", "Ice Breaker", "Cursed Speech", "Dismantle"])
      print(yuta_choices)
      if yuta_choices in ["Limitless", "Dismantle"]:
        heals += 4
      if yuta_choices in ["Ice Breaker", "Cursed Speech"]:
        heals += 6
      if yuta_choices in ["Jacob's Ladder"]:
        heals += 9
    self.hp += heals
    print(f"\n{self.name} used {move.name}")
    time.sleep(0.7)
    print(f"\n{self.name} healed {heals} hp")
    time.sleep(0.7)
    print(f"{self.name} is at {self.hp} hp")
    self.cooldown[move.name] = move.cooldown
    self.spend_ce(move.ce_cost)
    return True

  def suicide_move(self, enemy, move): #moves that result in a stalemate
    damage = 1000000
    enemy.hp = 0
    self.hp = 0
    print(f"\n{self.name} used {move.name}")
    time.sleep(0.7)
    print(f"\n{enemy.name} took {move.damage} damage")
    time.sleep(0.7)
    print(f"{enemy.name} is at {enemy.hp} hp")
    time.sleep(0.7)
    print(f"\n{self.name} is at {self.hp} hp")
    time.sleep(0.7)
    print(f"{self.name} destroyed the Battlefield")
    self.spend_ce(move.ce_cost)

  def handle_dodge(self, enemy, move): #the really complicated dodge mechanic
    dodge = random.randint(0, 100) #for dodge effect later in the code
    if enemy.boogie_woogie_dodge == True:
      if 35 <= dodge <= 75:
        print(f"\n{self.name} used {move.name}")
        time.sleep(0.7)
        print(f"{enemy.name} swapped positions with Boogie Woogie and dodged!")
        self.spend_ce(move.ce_cost)
        self.cooldown[move.name] = move.cooldown
        enemy.boogie_woogie_dodge = False
        return True
    else:
      if enemy.domain_name == "Time Cell Moon Palace":
        if 35 <= dodge <= 75:
          print(f"\n{enemy.name} moved through frames and dodged!")
          return True
      if enemy.name == "Naoya Zenin":
        if enemy.speed_stack >= 1:
          dodge_min = max(0, 52 - enemy.speed_stack)
          dodge_max = min(100, 58 + enemy.speed_stack)
          if dodge_min <= dodge <= dodge_max:
            print(f"{enemy.name} moved at impossible speeds, and dodged!")
            return True
      if enemy.name in ["Toji Fushiguro", "Maki Zenin", "Satoru Gojo"] and 47<= dodge <= 63: #special dodge rates
        print(f"\n{self.name} used {move.name}")
        if enemy.name == "Satoru Gojo":
          time.sleep(0.7)
          print(f"\n{enemy.name} dodged {move.name} with infinity")
        else:
          time.sleep(0.7)
          print(f"{enemy.name} dodged {move.name}")
        self.cooldown[move.name] = move.cooldown
        return True
      elif 52<= dodge <= 58: # the dodge effect comes into play
        print(f"\n{self.name} used {move.name}")
        time.sleep(0.7)
        print(f"{enemy.name} dodged {move.name}")
        self.spend_ce(move.ce_cost)
        self.cooldown[move.name] = move.cooldown
        return True
      return False

  def damage_attack(self, enemy, move, can_dodge = True): #normal attacks
    if move.name in ["Inverted Spear Of Heaven", "Soul Split Katana Slash"]:
      can_dodge = False
    if move.is_domain:
      self.activate_domain(move.name, 3)
      self.cooldown[move.name] = move.cooldown
      self.spend_ce(move.ce_cost)
      return True
    if move.name in CANNOT_DODGE_DOMAINS:
      can_dodge = False
    if can_dodge == True:
      if self.handle_dodge(enemy, move) == True:
        return True
    if self.name == "Kento Nanami":
      critical = random.randint(1, 10)
    else:
      critical = random.randint(0, 10) #random critical
    if self.name == "Kento Nanami":
      if self.hp <= self.max_hp // 2 and self.overtime == False:
        self.overtime = True
        time.sleep(0.7)
        print("\nNanami entered Overtime...")
    damage = max(0, random.randint(move.damage - 3, move.damage + 3))
    if critical == 10:
      damage = int(damage * move.crit)
      print(f"\n{self.name} entered the zone and hit a critical {move.name}")
    if critical != 10:
      print(f"\n{self.name} used {move.name}")
    if move.name == "Projection Sorcery":
      self.projection_active = True
      self.speed_stack += 1
      print(f"{self.name} accelerated with Projection sorcery!")
    if move.freeze:
      frozen = random.randint(0, 100)
      if frozen <= 45:
        enemy.frozen = True
    if self.name == "Choso Kamo":
      if move.blood:
        enemy.blood_stack += 1
        print(f"\n{enemy.name} gained a Blood Stack!")
        print(f"Blood Stacks: {enemy.blood_stack}")
    if self.name == "Toji Fushiguro":
      if enemy.domain_active == True:
        damage += 15
        print(f"Toji Fushiguro gets mildly affected by the domain.")
    if self.name == "Maki Zenin":
      if self.hp <= self.max_hp/2:
        damage += 10
        print("Maki Zenin enters a rage mode.")
    if enemy.domain_name == "Unlimited Void":
      damage = damage // 2
      damage = max(0, damage)
      print(f"{self.name} is stunned with infinite knowledge")
    if self.domain_name in ["Malevolent Shrine", "Chimera Shadow Garden"]:
      damage = int(damage * 1.225)
      if self.domain_name == "Malevolent Shrine":
        print(f"\n{enemy.name} gets cleaved and dismantled by the Shrine and Silas does a double back flip")
      else:
        extra = random.randint(4, 10)
        damage += extra
        print(f"\n{enemy.name} gets lost in the shadows and got attacked by some clones")
    if self.domain_name == "Authentic Mutual Love":
      damage += 4
      print(f"\n{enemy.name} gets hit by one of these techniques: ")
      yuta_choices = random.choice(["Limitless", "Jacob's Ladder", "Ice Breaker", "Cursed Speech", "Dismantle"])
      print(yuta_choices)
      if yuta_choices in ["Limitless", "Dismantle"]:
        damage += 6
      if yuta_choices in ["Ice Breaker", "Cursed Speech"]:
        damage += 4
      if yuta_choices in ["Jacob's Ladder"]:
        damage += 2
    if enemy.domain_name == "Chimera Shadow Garden":
      damage = damage // 3
      damage = max(0, damage)
      print(f"\nShadows are taking over {self}")
    if self.domain_name == "Celestial Star Forge":
      print(f"\n{enemy.name} gets crushed under the Star")
      damage = int(damage * 1.2) + 7
      self.hp -= 4
      print(f"\nYuki Tsukumo, herself gets damaged from her innate technique inside the domain, health: {self.hp}")
    if self.domain_name == "Womb Profusion":
      print("\nKenjaku creates a tree of grotesque human faces...")
      damage += 12
    if self.domain_name == "Self-Embodiment of Perfection":
      print("\nMahito shows the embodiment of his Perfection...")
      damage += 10
      self.hp += random.randint(7, 15)
      print(f"Mahito heals himself within the domain...\nMahito is at {self.hp} hp")
    if self.domain_name == "Coffin of The Iron Mountain":
      print("\nA Large Mountain spwels Lava. It is getting extremely hot")
      damage = max(int(damage * 1.5) - 6, 0)
    if self.domain_name == "Benevolent Shrine":
      print(f"\nHappy memories flood of {enemy.name} flood the domain.")
      self.hp += 12
      print(f"Yuji Itadori heals his soul from the domain, {self.hp} hp")
      damage = max(int((damage * 1.65) - 9), 0)
    if self.domain_name == "Time Cell Moon Palace":
      print(f"\n{enemy.name}'s cells are forced into frames!")
      freeze_chance = random.randint(1,100)
      if freeze_chance <= 45:
          enemy.frozen = True
          print(f"{enemy.name} failed to follow the 24 FPS rule and froze!")
      damage += self.speed_stack * 5
    if move.name == "Boogie Woogie":
      self.boogie_woogie_dodge = True
      time.sleep(0.7)
      print(f"\n{self.name} becomes unpredictable with {move.name}")
    if move.burn == True:
      burn_chance = random.randint(1, 100)
      if burn_chance <= 39:
        enemy.burn_turns = 2
        enemy.burn_damage = 8
        print(f"\n{enemy.name} was burned!")
    if move.name == "Supernova":
      damage += enemy.blood_stack * 6
      time.sleep(0.7)
      print(f"\nSupernova exploded {enemy.blood_stack} blood stacks!")
      enemy.blood_stack = 0
    if self.projection_active == True:
      damage += self.speed_stack * 5
    if enemy.simple_domain == True and self.domain_active == True:
      print(f"\n{enemy.name}'s Simple Domain disrupts the guaranteed-hit effect!")
      damage = int(damage * 0.5)
    elif enemy.simple_domain == True:
      time.sleep(0.7)
      print(f"\n{enemy.name}'s Simple Domain weakens the attack")
      damage = int(damage * 0.65)
    if enemy.soul_attack == True:
      if move.soul_resistence == False:
        time.sleep(0.7)
        print(f"\n{self.name}'s attack was innefective against {enemy.name} due to {enemy.name}'s soul resistance.")
        damage = int(damage * 0.89)
    if enemy.name == "Kenjaku":
      if damage >= 30:
        if random.randint(1,100) <= 39:
            damage = int(damage * 0.65)
            time.sleep(0.7)
            print("\nKenjaku used Anti-Gravity System to lessen the impact!")
    if self.name == "Kento Nanami" and self.overtime == True:
      damage += 5
    if self.name == "Kento Nanami":
      if move.name in ["Ratio Technique", "Collapsed Strike"]:
        weakpoint = random.randint(1,100)
        if weakpoint <= 45:
            print("\nNanami struck the 7:3 weak point!")
            damage += 5
    enemy.hp -= damage
    enemy.hp = max(0, enemy.hp) #prevents the hp from going below 0
    time.sleep(0.7)
    print(f"{enemy.name} took {damage} damage")
    time.sleep(0.7)
    print(f"{enemy.name} is at {enemy.hp} hp")
    self.spend_ce(move.ce_cost)
    self.cooldown[move.name] = move.cooldown
    return True

  def call_to_rika(self, enemy, cooldown, ce_cost): #special Yuta move aka pain in the butt vro
    yuta_list = [Move("Cleave and Dismantle", 30, 0, 0),Move("Hollow Purple", 40, 0, 0, crit = 2, soul_resistence=True),Move("Jacob's Ladder", -25, 0, 0),Move("Cursed Speech", 23, 0, 0),Move("Black Flash", 35, 0, 0, crit = 2)]
    print("\nChoose a move:")
    for i, move in enumerate(yuta_list): #enumerate keeps the track of index and still lets you loop
      print(f"{i+1}. {move.name} | Damage: {move.damage}")
      time.sleep(0.7)
    x = safe_int_input("Choose the move: ") - 1

    while x not in range(len(yuta_list)):
      print("Invalid move.")
      x = int(input("Choose a valid move: ")) - 1
    chosen_move= yuta_list[x]
    if self.handle_dodge(enemy, chosen_move) == True:
      return True
    if chosen_move.damage >= 0:
      self.damage_attack(enemy, chosen_move)
    else:
      self.heal(chosen_move)
    self.cooldown["Call to Rika"] = cooldown
    self.spend_ce(ce_cost)
    return True
  def call_to_rika_ai(self, enemy, cooldown, ce_cost): #The ai verson of the move
    yuta_list = [Move("Cleave and Dismantle", 30, 0, 0),Move("Hollow Purple", 40, 0, 0, crit = 2),Move("Jacob's Ladder", -25, 0, 0),Move("Cursed Speech", 23, 0, 0),Move("Black Flash", 35, 0, 0, crit = 2, soul_resistence=True)]
    if self.hp <=25:
      healing_moves = []
      if enemy.hp < 30:
        best_move = yuta_list[0] #the best move
        for moves in yuta_list:
          if moves.damage > best_move.damage:
            best_move = moves
        self.damage_attack(enemy, best_move)
        return True
      for moves in yuta_list:
        i, move_name, damage, ce_cost = moves
        if damage < 0:
          healing_moves.append(moves)
      if len(healing_moves) > 0:
        self.heal(random.choice(healing_moves)) #healing moves
        return True
    best_move = yuta_list[0] #the best move
    for moves in yuta_list:
      if moves.damage > best_move.damage:
        best_move = moves
    if self.handle_dodge(enemy, best_move) == True:
      return True
    if random.randint(1, 100) <= 25: #25 percent chance for randomness so that they dont always choose the strongest one
      self.damage_attack(enemy, random.choice(yuta_list))[0]
    else:
      self.damage_attack(enemy, best_move)#uses best move
    self.cooldown["Call to Rika"] = cooldown
    self.spend_ce(ce_cost)
    return True

  def attack(self, enemy, move_index): #the attack thing that calls other attacks
    move = self.moves[move_index]
    if move.name == "Focus":
      self.focus_ce()
      return True
    if self.ce<move.ce_cost:
      print(f"\nNot enough Cursed Energy for {move.name}")
      return False
    if self.on_cooldown(move) == True:
      return False
    if move.name == "Simple Domain":
      self.activate_simple_domain(2)
      self.cooldown[move.name] = move.cooldown
      self.spend_ce(move.ce_cost)
      return True
    if move.damage < 0:
      self.heal(move)
      return True
    if move.name in ["Divine General MAHORAGA", "Black Hole"]:
      self.suicide_move(enemy, move)
      return True
    if move.name == "Call to Rika":
      if self.ai == True:
        self.call_to_rika_ai(enemy, move.cooldown, move.ce_cost)
        return True
      else:
        self.call_to_rika(enemy, move.cooldown, move.ce_cost)
        return True
    if self.damage_attack(enemy, move) == True:
      return True

  def choose_move(self, enemy): #moves for the ai
    if self.name != "Toji Fushiguro" and self.name != "Maki Zenin":
      if self.ce <= 15:
        return "focus"
    available_moves = []
    for i in range(len(self.moves)):
      move = self.moves[i]
      if self.cooldown[move.name] == 0 and self.ce >= move.ce_cost:
        available_moves.append((i, move.name, move.damage, move.ce_cost)) #only allows the available moves in
    if len(available_moves) == 0:
      return "focus"
    if self.hp <=25:
      healing_moves = []
      if enemy.hp < 30:
        best_move = available_moves[0] #the best move
        for moves in available_moves:
          if moves.damage > best_move.damage:
            best_move = moves
        return best_move[0]
      for moves in available_moves:
        i, move_name, damage, ce_cost = moves
        if damage < 0:
          healing_moves.append(moves)
      if len(healing_moves) > 0:
        return random.choice(healing_moves)[0] #healing moves
    for moves in available_moves:
      i, move_name, damage, ce_cost = moves
      if move_name in DOMAIN_MOVES:
        if self.ce >= ce_cost:
          if enemy.hp <= 70 and self.hp <= 60:
            return i
    best_move = available_moves[0] #the best move
    for moves in available_moves:
      if moves[2] > best_move[2]:
        best_move = moves
    if random.randint(1, 100) <= 25: #25 percent chance for randomness so that they dont always choose the strongest one
      return random.choice(available_moves)[0]
    return best_move[0] #uses best move

  def reduce_domain(self): #reduces domain countdown
    if self.domain_active == True:
      self.domain_turns -= 1
      if self.domain_turns <= 0:
        print(f"\n{self.domain_name} faded away...")
        self.domain_active = False
        self.domain_name = ""

  def activate_domain(self, domain_name, turns): #activates the domain
    self.domain_active = True
    self.domain_turns = turns
    self.domain_name = domain_name
    print(f"\n{self.name} opened their domain: ")
    time.sleep(0.7)
    print(f"{domain_name}")
  def regain_ce(self): #passive CE regain
    regain = random.randint(2, 8)
    self.ce += regain
    self.ce = min(self.ce, self.max_ce)
    time.sleep(0.7)
    print(f"\n{self.name} regained {regain} CE")
  def reduce_cooldown(self): #reducing cooldowns for moves
      for move in self.cooldown:
        if self.cooldown[move] > 0:
          self.cooldown[move] -= 1
  def is_alive(self): #returns if teh character is alive or not
    return self.hp > 0
class Yuji(Jjk): #Our First character
  def __init__(self):
    super().__init__("Yuji Itadori", 162, 103, "Black Flashes have a 10 percent chance to do double damage. Simple Domain nullifies a chunk of damage.", "The Strongest of The Future")

    self.add_moves(Move("Divergent Fist", 17, 0, 10, soul_resistence=True), start_cd = 0) #His move list
    self.add_moves(Move("Black Flash", 35, 2, 25, crit = 2, soul_resistence=True), start_cd = 3)
    self.add_moves(Move("Cleave and Dismantle", 22, 1, 20), start_cd = 2)
    self.add_moves(Move("Blood Manipulation", 25, 3, 20), start_cd = 2)
    self.add_moves(Move("Reverse Cursed Technique", -20, 3, 20), start_cd = 2)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd = 2)
    self.add_moves(Move("Benevolent Shrine", 0, 5, 50,is_domain = True), start_cd = 5)

class Gojo(Jjk): #The honored one
  def __init__(self):
    super().__init__("Satoru Gojo", 144, 140, "Gojo has a 17 percent chance of dodging. Hollow Purple and Black Flash has a 10 percent chance to do double the damage. Simple Domain nullifies a chunk of damage.", "The Honored One")

    self.add_moves(Move("Blue", 20, 0, 15,soul_resistence=True), start_cd = 0) #move list
    self.add_moves(Move("Red", 30, 2, 25, soul_resistence=True), start_cd =1)
    self.add_moves(Move("Hollow Purple", 40, 3, 45, crit = 2, soul_resistence=True), start_cd = 3)
    self.add_moves(Move("Reverse Cursed Technique", -20, 3, 25), start_cd = 1)
    self.add_moves(Move("Black Flash", 35, 3, 25, crit = 2, soul_resistence=True), start_cd = 3)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd = 2)
    self.add_moves(Move("Unlimited Void", 0, 5, 35, is_domain = True),  start_cd = 5)

class Choso(Jjk): #The Big Blood Brother
  def __init__(self):
    super().__init__("Choso Kamo", 150, 93, "Save his blood stacks for supernova as the blood stacks can EXPLODE with Supernova dealing extra burst damage.", "The Blood Brother")

    self.add_moves(Move("Convergence", 20, 0, 15, blood = True), start_cd = 0)
    self.add_moves(Move("Piercing Blood", 23, 2, 17, blood = True), start_cd =2)
    self.add_moves(Move("Supernova", 20, 3, 20), start_cd = 2)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Slicing Exorcism", 31, 3, 21, blood = True), start_cd = 3)

class Maki(Jjk): #The Heavenly Restriction monster
  def __init__(self):
    super().__init__("Maki Zenin", 172, 0, "Soul Split Katana Slash cannot be dodged. She has extra damage when in low health.", "Zero Cursed Energy Empress")

    self.add_moves(Move("Polearms hit", 20, 0, 0),start_cd = 0)
    self.add_moves(Move("Mai's Wrath", 30, 1, 0),start_cd = 2)
    self.add_moves(Move("Focus", 0, 0, 0),start_cd = 0)
    self.add_moves(Move("Soul Split Katana Slash", 40, 3, 0),start_cd = 4)

class Megumi(Jjk): #The Potential Man
  def __init__(self):
    super().__init__("Megumi Fushiguro", 150, 103, "Divine General Mahoraga can force stalemates. Be careful.", "Potential Man")

    self.add_moves(Move("Divine Dogs", 18, 0, 12), start_cd = 0)
    self.add_moves(Move("Toad", 24, 2, 13),start_cd = 1)
    self.add_moves(Move("Max Elephant", 35, 3, 21),start_cd = 2)
    self.add_moves(Move("Round Dear", -24, 2, 15),start_cd = 0)
    self.add_moves(Move("Divine General MAHORAGA", 0, 10, 30), start_cd = 10)
    self.add_moves(Move("Focus", 0, 0, 0),start_cd = 0)
    self.add_moves(Move("Chimera Shadow Garden", 0, 5, 50, is_domain = True), start_cd = 5)

class Todo(Jjk): #The Besto Friendo
  def __init__(self):
    super().__init__("Aoi Todo", 168, 95, "Boogie Woogie has around a 20 percent chance to dodge. Use it before the opponent uses their trump card. Simple Domain nullifies a chunk of damage.", "The Loyal Besto Friendo")

    self.add_moves(Move("Boogie Woogie", 13, 2, 20),start_cd = 0)
    self.add_moves(Move("Black Flash", 35, 4, 25, crit = 2, soul_resistence=True), start_cd = 3)
    self.add_moves(Move("Besto Friendo", 20, 1, 0),start_cd = 1)
    self.add_moves(Move("Focus", 0, 0, 0),start_cd = 0)
    self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd = 2)
    self.add_moves(Move("Takada + Besto Friendo", 32, 2, 24), start_cd = 3)

class Yuki(Jjk): #The Star
  def __init__(self):
    super().__init__("Yuki Tsukumo", 162, 124, "Black Hole can force stalemates. Simple Domain nullifies a chunk of damage.", "The Star Vessel")

    self.add_moves(Move("Garudo Attack", 23, 0, 15), start_cd = 0)
    self.add_moves(Move("Mass Control", 27, 2, 20),start_cd = 1)
    self.add_moves(Move("Black Hole", 0, 10, 20),start_cd = 10)
    self.add_moves(Move("Reverse Cursed Technique", -20, 2, 25),start_cd = 1)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd =0)
    self.add_moves(Move("Simple Domain", 0, 4, 30), start_cd = 2)
    self.add_moves(Move("Celestial Star Forge", 0, 5, 50, is_domain = True), start_cd = 5)

class Yuta(Jjk): #Second to only Satoru Gojo
  def __init__(self):
    super().__init__("Yuta Okkotsu", 144, 146, "'Call to Rika' gives the user access to more copied techniques that can be used. Inside it, Hollow Purple and Black Flash have a 10 percent chance of doing double damage.", "The Prodigy")

    self.add_moves(Move("CE Reserve", 20, 0, 20), start_cd = 0)
    self.add_moves(Move("Slash", 23, 2, 25), start_cd = 1)
    self.add_moves(Move("Rika", 32, 4, 40), start_cd = 2)
    self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd = 1)
    self.add_moves(Move("Call to Rika", 0, 5, 40), start_cd = 1)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Authentic Mutual Love", 0, 5, 50, is_domain = True,), start_cd = 5)

class Nanami(Jjk): #Workaholic
  def __init__(self):
    super().__init__("Kento Nanami", 115, 110, "Has a bigger chance to hit a critical. When under half of max hp he hits overtime. Black Flash can hit a double critical, 'Ratio Technique' and 'Collapsed Strike' have their own criticals.", "The Workaholic")
    self.add_moves(Move("Ratio Technique", 26, 0, 15, crit = 1.53), start_cd = 0)
    self.add_moves(Move("Collapsed Strike", 34, 2, 25, crit = 1.6), start_cd = 2)
    self.add_moves(Move("Focus", 0, 0, 0),start_cd = 0)
    self.add_moves(Move("Black Flash", 35, 3, 25, crit = 2, soul_resistence=True), start_cd = 3)

class Sukuna(Jjk): #The king of Curses
  def __init__(self):
    super().__init__("Ryomen Sukuna", 180, 151, "Fuga has a random burning effect. Black Flash has a 10 percent chance of doing double damage.", "The King of Curses")

    self.add_moves(Move("Slash", 20, 0, 20), start_cd = 0)
    self.add_moves(Move("Dismantle", 30, 3, 23), start_cd = 2)
    self.add_moves(Move("Fuga", 36, 4, 35, burn = True), start_cd = 2)
    self.add_moves(Move("Black Flash", 35, 4, 25, crit = 2, soul_resistence=True), start_cd = 3)
    self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd = 1)
    self.add_moves(Move("World Cutting Slash", 100, 11, 150, soul_resistence=True),start_cd = 11)
    self.add_moves(Move("Focus", 0, 0, 0),start_cd = 0)
    self.add_moves(Move("Malevolent Shrine", 0, 5, 50, is_domain = True,), start_cd = 5)

class Toji(Jjk): #No Curse King
  def __init__(self):
    super().__init__("Toji Fushiguro", 174, 0, "Toji becomes stronger when the opponent opens their domain. Inverted Spear of Heaven can not be dodged.", "No Cursed Energy Monster")

    self.add_moves(Move("Punch", 20, 0, 0), start_cd = 0)
    self.add_moves(Move("Sword Slash", 30, 1, 0), start_cd = 2)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Inverted Spear Of Heaven", 40, 3, 0), start_cd = 4)

class Kenjaku(Jjk): #The immortal
  def __init__(self):
    super().__init__("Kenjaku", 149, 115, "Kenjaku has a chance to receive less damage when under a certain amount of HP.", "The Immortal")

    self.add_moves(Move("Cursed Spirit Manipulation", 20, 0, 15), start_cd = 0)
    self.add_moves(Move("Maximum: Uzumaki", 39, 4, 25), start_cd = 2)
    self.add_moves(Move("Antigravity System", 27, 3, 20), start_cd = 1)
    self.add_moves(Move("Reverse Cursed Technique", -20, 2, 30), start_cd = 1)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Womb Profusion", 0, 5, 50, is_domain = True), start_cd = 5)

class Mahito(Jjk): #The child curse
  def __init__(self):
    super().__init__("Mahito", 144, 103, "Black Flash can hit a double damage critical. Mahito receives less damage for MOST attacks.", "The Soul Shaper", soul_attack = True)

    self.add_moves(Move("Idle Transfiguration", 33, 3, 25), start_cd = 1)
    self.add_moves(Move("Black Flash", 35, 3, 25, crit = 2, soul_resistence=True), start_cd = 3)
    self.add_moves(Move("Morphing Punch", 12, 0, 15), start_cd = 0)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Self-Embodiment of Perfection", 0, 5, 50, is_domain = True,), start_cd = 5)

class Jogo(Jjk): #The Le jon of JJK
  def __init__(self):
    super().__init__("Jogo", 162, 106, "His first 3 attacks have a random burning effect.", "The Volcano")

    self.add_moves(Move("Disaster Flames", 20, 0, 15, burn = True), start_cd = 0)
    self.add_moves(Move("Ember Insects", 30, 2, 23, burn = True), start_cd = 2)
    self.add_moves(Move("Maximum: Meteor", 35, 3, 27, burn = True), start_cd = 1)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Coffin of The Iron Mountain", 0, 5, 50, is_domain = True,), start_cd = 5)

class Uraume(Jjk): #the forst queen
  def __init__(self):
    super().__init__("Uraume", 156, 103, "Her 'Frost Barrage' attack has a random chance of freezing her opponent for one turn.", "The Ice Queen")

    self.add_moves(Move("Icefall", 22, 0, 15), start_cd = 0)
    self.add_moves(Move("Frost Calm", 32, 2, 22), start_cd = 1)
    self.add_moves(Move("Frost Barrage", 27, 3, 30,  freeze = True), start_cd = 2)
    self.add_moves(Move("Focus", 0, 0, 0),start_cd = 0)
    self.add_moves(Move("Reverse Cursed Technique", -20, 2, 25), start_cd = 1)

class Naoya(Jjk): #the speedster
  def __init__(self):
    super().__init__("Naoya Zenin", 142, 109, "By using 'Projection Sorcery' the user can get 'faster' and do more damage that stacks with 'Mach 3 Tackle.' Frame Freeze has a chance of freezing the opponent for one turn.", "The Fastest")

    self.add_moves(Move("Projection Sorcery", 0, 2, 18), start_cd = 0)
    self.add_moves(Move("Frame Blitz", 24, 0, 15), start_cd = 0)
    self.add_moves(Move("Mach 3 Tackle", 42, 4, 35), start_cd = 2)
    self.add_moves(Move("Frame Freeze", 18, 3, 25,freeze = True),start_cd = 1)
    self.add_moves(Move("Focus", 0, 0, 0), start_cd = 0)
    self.add_moves(Move("Time Cell Moon Palace", 0, 5, 50, is_domain = True,), start_cd = 5)