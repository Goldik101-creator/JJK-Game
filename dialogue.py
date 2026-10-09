import random
 
from ui import say
 
SCENES = [
    {
        "left": {"Satoru Gojo"},
        "right": {"Ryomen Sukuna"},
        "intro": "\nShinjuku Showdown happening all over again: \nThe Honored One against the King of Curses",
        "variants": [
            {"lines": [
                "\nSatoru Gojo: The only reason why you WERE considered the strongest, \nWas because I wasn't born yet",
                "\nRyomen Sukuna: We will see...'The Honored One'\nThere is a reason why Sukuna was called the King of Curses...",
            ]},
            {"lines": [
                "\nRyomen Sukuna: Oh how far we have fallen as Jujutsu Sorcerers, \nI will bring back the Golden Heian Era to Japan once again!",
                "\nSatoru Gojo: Nah, I'd win... \nIt will take much to force the Honored one to try...",
            ]},
        ],
    },
    {
        "left": {"Yuji Itadori", "Choso Kamo"},
        "right": {"Kenjaku"},
        "intro": "\nThe immortal sorcerer sees his child",
        "variants": [
            {"lines": [
                "\n{character}: You ruined EVERYTHING FOR US",
                "\nKenjaku: How could I ruin it? \nI wasn't even there",
            ]},
            {"lines": [
                "\nKenjaku: What a foolish thing it is to do. To protect your brother",
                "\n{character}: The older brothers pave the road, \nWhile younger ones follow it.\nI will avenge my brother",
            ]},
        ],
    },
    {
        "left": {"Yuji Itadori"},
        "right": {"Ryomen Sukuna"},
        "intro": "\nThe Vessel of Sukuna fighting his own Master",
        "variants": [
            {"lines": [
                "\nYuji Itadori: I will fight for Megumi, and Master Gojo",
                "\nRyomen Sukuna: You goddamn brat, \nDo not look down on me! I am a curse!",
            ]},
            {"lines": [
                "\nRyomen Sukuna: Your kindness for others won't take you far, child",
                "\nYuji Itadori: Even if none of this is my fault,\nThere is no way I can convince myself otherwise!",
            ]},
        ],
    },
    {
        "left": {"Yuta Okkotsu"},
        "right": {"Toji Fushiguro", "Kenjaku"},
        "intro": "\nThe Enemy of Jujutsu High faced the Sorcerer, second to only Satoru Gojo",
        "variants": [
            {"lines": [
                "\nYuta Okkotsu: You are the sorcerer that drove Master Gojo into a corner... \n{enemy}, right?",
                "\n{enemy}: You are smart... \nIt saddens me that I have to kill you.",
                "\nYuta Okkotsu: You don't have to kill me though",
                "\n{enemy}: Where is the fun in that?",
            ]},
            {"enemy": "Toji Fushiguro", "lines": [
                "\nYuta Okkotsu: You have no cursed energy, just like Maki",
                "\nToji Fushiguro: Don't underestimate me child",
                "\nYuta Okkotsu: I would never underestimate someone like Maki",
            ]},
            {"enemy": "Kenjaku", "lines": [
                "\nYuta Okkotsu: you are not Suguru Geto. I killed him. \nWhat are you?",
                "\nKenjaku: I go by many names. You can call me Kenjaku",
                "\nYuta Okkotsu: I do not care what your name is. \nI only care that my teacher won't have to see me kill the face of his best friend twice...",
            ]},
        ],
    },
    {
        "left": {"Satoru Gojo"},
        "right": {"Toji Fushiguro"},
        "intro": "\nSatoru Gojo Picks up Toji Zenin's location through the Six Eyes",
        "variants": [
            {"lines": [
                "\nToji Zenin: Damn your Six Eyes. How can you perceive me while I have no cursed energy?",
                "\nSatoru Gojo: If you live constantly with white noise, and you notice a location with the absence of that noise, \nWouldn't you also notice?\nToji Fushiguro?",
            ]},
            {"lines": [
                "\nSatoru Gojo: Coming back from the deceased, huh? With your old toys too. Inverted Spear of Heaven...",
                "\nToji Zenin: I am not falling for your tricks again, Satoru. Keep that Limitless Technique off, since this toy as you say doesn't obey Infinity.",
                "\nSatoru Gojo: We will see about that...",
            ]},
            {"lines": [
                "\nSatoru Gojo: Do you remember Riko, the star plasma vessel.\nAnd everything you stole from us? Cutting the strings of Fate from us?",
                "\nToji Zenin: Why would I remember something as minor as that? Satoru",
            ]},
        ],
    },
    {
        "left": {"Satoru Gojo"},
        "right": {"Kenjaku"},
        "intro": "\nSatoru Gojo sees his dead friend.",
        "variants": [
            {"lines": [
                "\nSatoru Gojo: Suguru? Is that you...",
                "\nKenjaku: Hey, Satoru, long time no see?",
                "\nSatoru Gojo: You are not Suguru. What are you...",
                "\nKenjaku: Sorry Six Eyes bearer, but your time is up",
            ]},
            {"lines": [
                "\nKenjaku: Satoru...",
                "\nSatoru Gojo: Suguru. You are not Suguru \nWho are you?",
                "\nKenjaku: I will show you right before you take your final breath, Satoru. ",
            ]},
        ],
    },
    {
        "left": {"Yuji Itadori"},
        "right": {"Mahito"},
        "intro": "\nThe young curse sees Yuji once again",
        "variants": [
            {"lines": [
                "\nMahito: YUUUUUUJI ITADORIIIII",
                "\nYuji Itadori: Oh, you again \nHave you always been this weak?",
                "\nMahito: OH DO NOT UNDERESTIMATE ME!",
            ]},
        ],
    },
    {
        "left": {"Toji Fushiguro"},
        "right": {"Maki Zenin"},
        "intro": "\nCursless man sees someone who may match his Heavenly Restriction",
        "variants": [
            {"lines": [
                "\nToji Fushiguro: Do I know you? You are just like me...",
                "\nMaki Zenin: I don't think you can just stop me. I killed my entire clan after all",
            ]},
            {"lines": [
                "\nMaki Zenin: Oh god...are you another Zenin? You look like one of my cousin.",
                "\nToji Fushiguro: Don't ever call me that name if you value your own life, child",
            ]},
        ],
    },
]
 
 
def find_scene(name_a, name_b):
    for scene in SCENES:
        if name_a in scene["left"] and name_b in scene["right"]:
            return scene, name_a, name_b
        if name_b in scene["left"] and name_a in scene["right"]:
            return scene, name_b, name_a
    return None
 
 
def play_dialogue(p1, p2):
    found = find_scene(p1.name, p2.name)
    if found is None:
        say(f"\n{p1.name} sees {p2.name}")
        say(f"\n{p1.name}: Oh, you will regret stepping up against me...")
        say(f"{p2.name}: I won't regret it if I destroy you first.")
        return
 
    scene, character, enemy = found
    eligible = [v for v in scene["variants"] if v.get("enemy") in (None, enemy)]
    variant = random.choice(eligible)
    say(scene["intro"])
    for line in variant["lines"]:
        say(line.format(character=character, enemy=enemy))
 