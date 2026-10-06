
import random
import time
from utilities import safe_int_input
from characters import Yuji, Gojo, Sukuna, Yuta, Yuki, Megumi, Todo, Choso, Naoya, Uraume, Nanami, Maki, Toji, Jogo, Mahito, Kenjaku
from dialogue import dialogue
list_characters = {"Yuji": Yuji(), "Gojo": Gojo(), "Yuta": Yuta(), "Choso": Choso(), "Yuki": Yuki(), "Todo": Todo(), "Megumi": Megumi(), "Maki": Maki(), "Sukuna": Sukuna(), "Toji": Toji(), "Kenjaku": Kenjaku(), "Mahito": Mahito(), "Jogo": Jogo(), "Uraume": Uraume(), "Naoya": Naoya(), "Nanami":Nanami()}
def status(character, enemy, turn): #Creates the status at where everyone is at
  if turn > 1:
    print(f"\n\n{character} is at {character.hp} while {enemy} is at {enemy.hp}")
def fight_person(character, enemy): #The person fighting 
    character.show_moves() #shows the moves to choose

    move_number = safe_int_input("Choose the move: ")

    while move_number not in range(1, len(character.moves)+1):
      print("Not a move")
      move_number = safe_int_input("Choose the move: ")
    if character.frozen == True:
      time.sleep(0.7)
      print(f"{character.name} is frozen and cannot move!")
      character.frozen = False
    else:
      success = character.attack(enemy, move_number-1) #checks if the move is on cooldown or not
      while success == False:
        move_number = safe_int_input("Choose the move: ") #makes you choose another move
        while move_number not in range(1, len(character.moves) +1):
          print("Not a move.")
          move_number = safe_int_input("Choose the move: ")
        success = character.attack(enemy, move_number-1)
    character.reduce_domain()
    character.reduce_simple_domain()
def fight_ai(enemy, character): #ai fights
  if enemy.is_alive() and character.is_alive(): #so that the villian cant attack after they die
      if enemy.frozen == True:
        time.sleep(0.7)
        print(f"{enemy.name} is frozen and cannot move!")
        enemy.frozen = False
      else:
        move_number = enemy.choose_move(character)
        if move_number == "focus":
          enemy.focus_ce()
        else:
          enemy.attack(character, move_number)
      enemy.reduce_domain()
      enemy.reduce_simple_domain()
def one_vs_one_game(): #The main game
  print("Choose the Character: ") #makes you choose a character
  print(*list_characters.keys())
  character = input("").capitalize()
  character_chosen = False
  while character_chosen == False: #checks every character
    if character in list_characters.keys():
      character_key = character
      character = list_characters[character]
      character_chosen = True
    else:
      print("Not a character. Pick a character again: ")
      print(*list_characters.keys())
      character = input("").capitalize()
  del list_characters[character_key]
  enemy = random.choice(list(list_characters.values()))
  enemy.ai = True
  print(f"You chose {character}---{character.title}")
  print(f"Tip: {character.tip}")
  print(f"The enemy is {enemy}---{enemy.title}")
  turn = 1
  dialogue(character.name, enemy.name)
  print()
  enemy.show_moves()

  while character.is_alive() == True and enemy.is_alive() == True: #while both characters are alive, they fight

    print(f"\nTurn {turn} ")
    status(character, enemy, turn)
    fight_person(character, enemy)

    fight_ai(enemy, character)
    turn += 1
    character.reduce_cooldown() #reduces the cooldown by 1 every turn
    enemy.reduce_cooldown()
    character.apply_status_effect(enemy)
    enemy.apply_status_effect(character)
    if character.is_alive() and enemy.is_alive():
      if character.name not in ["Maki Zenin", "Toji Fushiguro"]:
        character.regain_ce()
      if enemy.name not in ["Maki Zenin", "Toji Fushiguro"]:
        enemy.regain_ce()
  if enemy.is_alive(): #endings
    print(f"\n{character} failed... You lost.")
  elif not enemy.is_alive() and not character.is_alive() :
    print(f"\n{character} and {enemy} both failed.")
  else:
    print(f"\n{character} succeeded against {enemy}. You won.")

def sandbox(): #ai vs ai fight
  turn = 0
  print("Choose your character to fight: ")
  print(*list_characters)
  character = input("").capitalize()
  character_chosen = False
  while character_chosen == False: #checks every character
    if character in list_characters.keys():
      character_key = character
      character = list_characters[character]
      character_chosen = True
    else:
      print("Not a character. Pick a character again: ")
      print(*list_characters.keys())
      character = input("").capitalize()
  del list_characters[character_key]
  print("Choose your other character to fight: ")
  print(*list_characters)
  enemy = input("").capitalize()
  character_chosen = False
  while character_chosen == False: #checks every character
    if enemy in list_characters.keys():
      enemy = list_characters[enemy]
      character_chosen = True
    else:
      print("Not a character. Pick a character again: ")
      print(*list_characters.keys())
      enemy = input("").capitalize()
  print(f"{character.name}---{character.title}\nVS\n{enemy.name}---{enemy.title}")
  dialogue(character.name, enemy.name)
  character.ai = True
  enemy.ai = True

  while character.is_alive() and enemy.is_alive():
    turn += 1
    print(f"Turn {turn}")
    status(character, enemy, turn)
    fight_ai(character, enemy)
    time.sleep(2.5)
    fight_ai(enemy, character)
    time.sleep(2.5)
    character.reduce_cooldown() #reduces the cooldown by 1 every turn
    enemy.reduce_cooldown()
    character.apply_status_effect(enemy)
    enemy.apply_status_effect(character)
    if character.is_alive() == True and enemy.is_alive() == True:
      if character.name not in ["Maki Zenin", "Toji Fushiguro"]:
        character.regain_ce()
      if enemy.name not in ["Maki Zenin", "Toji Fushiguro"]:
        enemy.regain_ce()
  if character.is_alive() == False and enemy.is_alive() == False:
    return "Draw", turn
  if character.is_alive() == False:
    return character.name, turn
  if enemy.is_alive() == False:
    return enemy.name, turn

def player_vs_player(): #both players fighting
  print("Choose the Character For Player 1: ") #makes you choose a character
  print(*list_characters.keys())
  character = input("").capitalize()
  character_chosen = False
  while character_chosen == False: #checks every character
    if character in list_characters.keys():
      character_key = character
      character = list_characters[character]
      character_chosen = True
    else:
      print("Not a character. Pick a character again: ")
      print(*list_characters.keys())
      character = input("").capitalize()
  del list_characters[character_key]
  print("Choose the Character For Player 2: ") #makes you choose a character
  print(*list_characters.keys())
  enemy = input("").capitalize()
  character_chosen = False
  while character_chosen == False: #checks every character
    if enemy in list_characters.keys():
      enemy_key = enemy
      enemy = list_characters[enemy]
      character_chosen = True
    else:
      print("Not a character. Pick a character again: ")
      print(*list_characters.keys())
      enemy = input("").capitalize()
  print(f"\nFirst Player: {character}---{character.title}")
  print(f"Tip: {character.tip}")
  print(f"\nThe Second Player: {enemy}---{enemy.title}")
  print(f"Tip: {enemy.tip}")
  dialogue(character.name, enemy.name)
  turn = 1
  while character.is_alive() and enemy.is_alive():
    print(f"Turn: {turn}")
    status(character, enemy, turn)
    if character.is_alive():
      fight_person(character, enemy)
    if enemy.is_alive():
      fight_person(enemy, character)
    turn += 1
    character.reduce_cooldown() #reduces the cooldown by 1 every turn
    enemy.reduce_cooldown()
    character.apply_status_effect(enemy)
    enemy.apply_status_effect(character)
    if character.is_alive() and enemy.is_alive():
      if character.name not in ["Maki Zenin", "Toji Fushiguro"]:
        character.regain_ce()
      if enemy.name not in ["Maki Zenin", "Toji Fushiguro"]:
        enemy.regain_ce()
  if enemy.is_alive(): #endings
    print(f"\n{character} failed... {enemy} won.")
  elif not enemy.is_alive() and not character.is_alive() :
    print(f"\n{character} and {enemy} both failed.")
  else:
    print(f"\n{character} succeeded against {enemy}. You won.")