from characters import Yuji, Gojo, Sukuna, Yuta, Yuki, Megumi, Todo, Choso, Naoya, Uraume, Nanami, Maki, Toji, Jogo, Mahito, Kenjaku
from utilities import safe_int_input
from game_modes import one_vs_one_game, sandbox, player_vs_player
import time
import random

#the start of the main code
print("Welcome to JJK, sorceror! ")
first_answer = ""
first_answer = input("Do you wanna know the info about the game, before we start? Yes for yes and anything for no ").lower()
if first_answer == "yes":
  print("To use an attack put the number of that is associated with that attack. \nAt the start of each turn you can see the health of your character and their cursed energy with their MAX cursed energy. \nNegative damage indicate healing. \nIf the damage has 0 and has the name the Divine General Mahoraga and Black hole then it is a suicide move. \nIf the last move of the character has 0 damage it is a domain expansion, use that wisely. \nThe middle columb indicates the cost of that move. Cannot use that move if you don't have the Cursed Energy. \nThe last column indicates the cooldown of that character. \nIf you have little cursed energy left use 'Focus' to regain a lot of cursed energy. \nThe damage indicated on the character is on a +-3 damage range, same with the healing. \nThere is a ten percent chance to hit a critical shot that does 1.5x damage for MOST attacks. \nDodge rate is around 9 percent for MOST characters.")
else:
  print('\nThen you must be a veteran! ')

game = safe_int_input("Choose your game moode, type 1 for player vs ai, 2 for ai vs ai, and 3 for player vs player: \n")
if game == 1:
  one_vs_one_game()
elif game == 2:
  sandbox()
elif game == 3:
  player_vs_player()
else:
  print("Really? Nothing...")