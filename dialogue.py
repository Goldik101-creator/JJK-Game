import time
import random
def dialogue(character, enemy): 
  if character == "Satoru Gojo" and enemy == "Ryomen Sukuna":
      time.sleep(0.7)
      print("\nShinjuku Showdown happening all over again: \nThe Honored One against the King of Curses")
      randomness = random.randint(1, 2)
      if randomness == 1:
        time.sleep(0.7)
        print("\nSatoru Gojo: The only reason why you WERE considered the strongest, \nWas because I wasn't born yet")
        time.sleep(0.7)
        print("\nRyomen Sukuna: We will see...'The Honored One'\nThere is a reason why Sukuna was called the King of Curses...")
      else:
        time.sleep(0.7)
        print("\nRyomen Sukuna: Oh how far we have fallen as Jujutsu Sorcerers, \nI will bring back the Golden Heian Era to Japan once again!")
        time.sleep(0.7)
        print("\nSatoru Gojo: Nah, I'd win... \nIt will take much to force the Honored one to try...")

  elif character in ["Yuji Itadori", "Choso Kamo"] and enemy == "Kenjaku":
      time.sleep(0.7)
      print("\nThe immortal sorceror sees his child")
      randomness = random.randint(1, 2)
      if randomness == 1:
        time.sleep(0.7)
        print(f"\n{character}: You ruined EVERYTHING FOR US")
        time.sleep(0.7)
        print("\nKenjaku: How could I ruin it? \nI wasn't even there")
      else:
        time.sleep(0.7)
        print("\nKenjaku: What a foolish thing it is to do. To protect your brother")
        time.sleep(0.7)
        print(f"\n{character}: The older brothers pave the road, \nWhile younger ones follow it.")
        time.sleep(0.7)
        print("I will avenge my brother")

  elif character == "Yuji Itadori" and enemy == "Ryomen Sukuna":
      time.sleep(0.7)
      print("\nThe Vessel of Sukuna fighting his own Master")
      randomness = random.randint(1, 2)
      if randomness == 1:
        time.sleep(0.7)
        print("\nYuji Itadori: I will fight for Megumi, and Master Gojo")
        time.sleep(0.7)
        print("\nRyomen Sukuna: You goddamn brat, \nDo not look down on me! I am a curse!")
      else:
        time.sleep(0.7)
        print("\nRyomen Sukuna: Your kindness for others won't take you far, child")
        time.sleep(0.7)
        print("\nYuji Itadori: Even if none of this is my fault,\nThere is no way I can convince myself otherwise!")

  elif character == "Yuta Okkotsu" and enemy in ["Toji Fushiguro", "Kenjaku"]:
      time.sleep(0.7)
      print("\nThe Enemy of Jujutsu High faced the Sorceror, second to only Satoru Gojo")
      randomness = random.randint(1, 2)
      if randomness == 1:
        time.sleep(0.7)
        print(f"\nYuta Okkotsu: You are the sorceror that drove Master Gojo into a corner... \n{enemy}, right?")
        time.sleep(0.7)
        print(f"\n{enemy}: You are smart... \nIt saddens me that I have to kill you.")
        time.sleep(0.7)
        print("\nYuta Okkotsu: You don't have to kill me though")
        time.sleep(0.7)
        print(f"\n{enemy}: Where is the fun in that?")
      else:
        if enemy == "Toji Fushiguro":
          time.sleep(0.7)
          print("\nYuta Okkotsu: You have no cursed energy, just like Maki")
          time.sleep(0.7)
          print("\nToji Fushiguro: Don't underestimate me child")
          time.sleep(0.7)
          print("\nYuta Okkotsu: I would never underestimate someone like Maki")
        else:
          time.sleep(0.7)
          print("\nYuta Okkotsu: you are not Suguru Geto. I killed him. \nWhat are you?")
          time.sleep(0.7)
          print("\nKenjaku: I go by many names. You can call me Kenjaku")
          time.sleep(0.7)
          print("\nYuta Okkotsu: I do not care what your name is. \nI only care that my teacher won't have to see me kill the face of his best friend twice...")

  elif character == "Satoru Gojo" and enemy == "Toji Fushiguro":
      time.sleep(0.7)
      print("\nSatoru Gojo Picks up Toji Zenin's location through the Six Eyes")
      randomness = random.randint(1, 3)
      if randomness == 1:
        time.sleep(0.7)
        print(f"\nToji Zenin: Damn your Six Eyes. How can you percieve me while I have no cursed energy?")
        time.sleep(0.7)
        print("\nSatoru Gojo: If you live constantly with white noise, and you notice a location with the absence of that noise, \nWouldn't you also notice?")
        time.sleep(0.7)
        print("Toji Fushiguro?")
      elif randomness == 2:
        time.sleep(0.7)
        print("\nSatoru Gojo: Coming back from the deceased, huh? With your old toys too. Inverted Spear of Heaven...")
        time.sleep(0.7)
        print(f"\nToji Zenin: I am not falling for your tricks again, Satoru. Keep that Limitless Technique off, since this toy as you say doesn't obey Infinity.")
        time.sleep(0.7)
        print("\nSatoru Gojo: We will see about that...")
      else:
        time.sleep(0.7)
        print("\nSatoru Gojo: Do you remember Riko, the star plasma vessel.")
        time.sleep(0.7)
        print("And everything you stole from us? Cutting the strings of Fate from us?")
        time.sleep(0.7)
        print("\nToji Zenin: Why would I remember something as minor as that? Satoru")

  elif character == "Satoru Gojo" and enemy == "Kenjaku":
      time.sleep(0.7)
      print("\nSatoru Gojo sees his dead friend.")
      randomness = random.randint(1, 2)
      if randomness == 1:
        time.sleep(0.7)
        print(f"\nSatoru Gojo: Suguru? Is that you...")
        time.sleep(0.7)
        print("\nKenjaku: Hey, Satoru, long time no see?")
        time.sleep(0.7)
        print("\nSatoru Gojo: You are not Suguru. What are you...")
        time.sleep(0.7)
        print("\nKenjaku: Sorry Six Eyes bearer, but your time is up")
      elif randomness == 2:
        time.sleep(0.7)
        print("\nKenjaku: Satoru...")
        time.sleep(0.7)
        print(f"\nSatoru Gojo: Suguru. You are not Suguru \nWho are you?")
        time.sleep(0.7)
        print("\nKenjaku: I will show you right before you take your final breath, Satoru. ")

  elif character == "Yuji Itadori" and enemy == "Mahito":
      time.sleep(0.7)
      print("\nThe young curse sees Yuji once again")
      time.sleep(0.7)
      print(f"\nMahito: YUUUUUUJI ITADORIIIII")
      time.sleep(0.7)
      print("\nYuji Itadori: Oh, you again \nHave you always been this weak?")
      time.sleep(0.7)
      print("\nMahito: OH DO NOT UNDERESTIMATE ME!")