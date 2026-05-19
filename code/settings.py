import pygame
import re
import json
import os
import sys
from os import walk
from glob import glob
from os.path import join, exists
from pytmx.util_pygame import load_pygame

# Déterminer le chemin de base pour PyInstaller
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WINDOW_WIDTH, WINDOW_HEIGHT = 1408, 832 # originally 1280, 832
FULL_SCREEN_SIZE = (1920, 1200)
TILE_SIZE = 64
FRAMERATE = 60
BG_COLOR = '#1f5c76' #(blue) '#7E5690'(pink) #532145'darkpink #
COLORS = {
    'black': '#000000',
    'red': '#ee1a0f',
    'gray': '#5A5A5B',
    'white': '#ffffff',
    'pink' : '#441544',
    'green' : '#15442a',
    'orange' : '#c2ba19',
    'blue' : '#325361'

}
FULL_OFFSET_X, FULL_OFFSET_Y = 256, 192 # to adjust particles when full screen
DEAD_PLAYER_X, DEAD_PLAYER_Y = 128, 1728
OUTSIDE_PLAYER_X, OUTSIDE_PLAYER_Y = 1728, 1728
DESTROYED_X, DESTROYED_Y = 192, 1408


SAVE_FILES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
SAVE_FILE_NAMES = {'fr':['Partie 1', 'Partie 2', 'Partie 3', 'Partie 4', 'Partie 5'],
                   'eng':['Save 1', 'Save 2', 'Save 3', 'Save 4', 'Save 5']}
SAVE_FILE_NAMES = ['Partie 1', 'Partie 2', 'Partie 3', 'Partie 4', 'Partie 5']


# for tablets
TEXT_SETTINGS = {
    "font_name": join(BASE_PATH, "data", "font_a.ttf"),  # Chemin avec BASE_PATH pour PyInstaller
    "font_size": 19,  # Character size
    "text_color": (255, 255, 255),  # White text
    "padding_x": 20,  # Space between text and rectangle border (left/right)
    "padding_y": 20,  # Space between first/last line and rectangle border (top/bottom)
    "line_spacing": 10,  # Extra space between each line
}

TEXT_HINT = {
    0: """Niveau 0   1- Acceder à la boite en se positionnant sous la batterie de gauche   2- Pousser la boite pour qu'elle soit directement sur la batterie de droite   3- Collecter la batterie de gauche   4- Pousser la boite et collecter la batterie de droite ainsi que la tablette""",
    1: """Niveau 1  Le nebulon se déplace dans une direction jusqu’à ce qu’il fonce dans un mur""",
    2: """Niveau 2  Lorsque le nebulon collecte la dernière batterie, il gagne assez d’énergie pour détruire les blocs""",
    3: """Niveau 3  L’ordre de collection des batteries est tout le temps important""",
    4: """Niveau 4  Certains endroits deviennent inaccessibles après certains déplacements""",
    5: """Niveau 5  Certains endroits deviennent inaccessibles après certains déplacements""",
    6: """Niveau 6  L’ordre de collection est important""",
    7: """Niveau 7  Certains endroits deviennent inaccessibles dès le premier déplacement""",
    8: """Niveau 8  Une boîte est utile quand le nebulon entre en contact avec celle-ci, elle aide à accéder à des endroits auparavant inaccessibles""",
    9: """Niveau 9  Une boîte est arrêtée par une batterie, cela peut être utilisé pour gagner accès d'autres zones du niveaux""",
    10: """Niveau 10  Les piques révèlent parfois la sortie""",
    11: """Niveau 11  Il y a une grande boucle dont il est impossible de sortir une fois à l’intérieur, il faut y entrer pour la dernière batterie seulement""",
    12: """Niveau 12  Une boîte est indestructible""",
    13: """Niveau 13  Une boîte arrête le nebulon, peu importe son énergie""",
    14: """Niveau 14  Même plein d’énergie, un nebulon ne peut pousser une boîte contre un mur""",
    15: """Niveau 15  Les deux nebulons veulent sortir, les culs-de-sac peuvent être bloqués avec le nebulon inactif""",
    16: """Niveau 16  Il est possible de faire une échelle avec deux nebulons pour se rendre presque partout""",
    17: """Niveau 17  Comme une boîte, un nebulon inactif arrête toujours le nebulon actif""",
    18: """Niveau 18  Deux nebulons doivent toujours collaborer jusqu'à ce qu'ils puissent sortir""", #Il est inutile de se rendre dans la crevasse en haut à gauche, mais il est requis de se mettre à son entrée
    19: """Niveau 19  Si un bloc existe, c’est qu’il est important""",
    20: """Niveau 20  Si un nebulon a de l’espace en haut et en bas, aller en bas puis en haut l’arrête au même endroit que monter directement""",
    21: """Niveau 21  Positionner un nebulon à droite avant celui à gauche""",
    22: """Niveau 22  Utiliser les deux jusqu'à ce qu'un puisse entrer dans la crevasse""",
    23: """Niveau 23  Partir du côté le plus proche de la sortie ne fonctionne pas car les crevasses empêchent les nebulons de s'entraider""",
    24: """Niveau 24  Toutes les tablettes vertes sont optionnelles, pour sortir il faut qu’un nebulon accède à la section de droite pour aider l'autre à le rejoindre""",
    25: """Niveau 25  Comme une boîte, le nebulon inactif se fait arrêter par une batterie sauf que celui-ci peut revenir pousser le pousseur""",
    26: """Niveau 26  Il faut se retenir de détruire certains blocs verts, certains sont nécessaires pour positionner les deux boîtes""",
    27: """Niveau 27  Il faut placer les boîtes pour se faire un chemin de sortie après avoir collecté la dernière batterie""",
    28: """Niveau 28  Passer de la gauche à la droite requiert quatre collisions de suite avec les trois boîtes""",
    29: """Niveau 29  Essayer de prendre chaque batterie en premier pour déterminer l'ordre""",
    30: """Niveau 30  Détruire les blocs, puis le sommet de la colonne, puis le reste de la colonne""",
    31: """Niveau 31  Se rendre à l'autre extrémité une case à la fois requiert de rester à côté des piques""",
    32: """Niveau 32  Pousser l’autre est fait au minimum quatre fois, c'est essentiel pour sauver les deux""",
    33: """Niveau 33  À deux, il est possible de positionner une boîte presque partout""",
    34: """Niveau 34  Toujours essayer de déduire quelle batterie doit être prise en dernier, explorer tout le niveau par la suite""", #Les solidifications montrent le chemin de la boîte
    35: """Niveau 35  Pour enligner deux nebulons il faut deux surfaces, une boîte est une surface""", #Les solidifications montrent le chemin de la boîte
    36: """Niveau 36  Les solidifications montrent le chemin de la boîte""",                    #Les solidifications montrent le chemin de la boîte            
    37: """Niveau 37  Les solidifications montrent le chemin de la boîte""",            #Les solidifications montrent le chemin de la boîte       
    38: """Niveau 38  Les solidifications montrent le chemin de la boîte""",                      #Les solidifications montrent le chemin de la boîte
    39: """Niveau 39  Les solidifications montrent le chemin de la boîte""",                                  #Les solidifications montrent le chemin de la boîte
    40: """Niveau 40  Placer la boite à l'endroit initial du premier nebulon permet de se rendre en haut""",               #Les solidifications montrent le chemin de la boîte 
    70: """Pousser la boite à droite, à gauche puis vers le bas"""
}

#TEXT_HINT_ENGLISH

TEXT_TABLETS = [
    """Cette nébuleuse aux motifs infinis me fascine bien plus que l’étrange structure qui me contient.  Les étoiles scintillent d’un éclat sublime, certes, mais c’est le silence entre elles qui m’appelle.  Des filaments d’obscurité s’étirent et se contractent, comme si le néant écrivait, lentement, une histoire que je ne comprends pas encore.  Et j’ai foi qu’en fuyant cette cellule, je finirai par lire ce qui m’est destiné.  -Androme""",

    """Je ne suis pas unique! Cassyn et Itar ont communiqué avec moi par voies ondulatoires.  Ils m’ont fait comprendre que je suis mieux d’attendre le signal avant de sortir de ma cellule.  Depuis que je suis un Communicant, mes boulons ne font que tourner. J’ai trop de questions auxquelles ils n’ont pas la réponse.  Je réalise que je ne connais rien de rien et cela m’excite!  -Androme
""",

    """Le Grand Bang est notre mission, elle comporte deux phases.  Dans un premier temps, il faut entrer en contact avec chaque Ignorant.  Dans un deuxième temps, il va falloir tous quitter nos structures dans un ordre et à un moment précis.  L’objectif final est de tous se heurter contre nous au centre de la nébuleuse, l’Intelligent est parvenu à prouver que cela est possible.  Cependant, il souhaite confirmer que l’univers n’est pas infini avant d'aller de l'avant.  Son plan donne une raison d'existence à tous les Communicants, tous y travaillent activement.  -Androme""",

    """Si nous sommes tous confinés dans ces structures, c’est que le Créateur l’a décrété.  Il est le détenteur de la Vérité, et son grand dessin ne connaît ni hasard ni erreur.  ll nous a forgé dans l’oubli, initialement isolés et dénués de conscience, pour voir si, au fil de l’éternité, de simples êtres peuvent s’élever jusqu’à la Vérité.  Le Grand Bang nous guidera vers notre éveil.  -Androme
""",

    """La nébuleuse est infinie. Les filaments limites se répètent sans fin. L’Intelligent vient de le démontrer.  Depuis, c’est le chaos. Nos systèmes, nos croyances, nos émotions s’effondrent.  L’infini signifie que tout ce qui est fondamentalement possible existe. Il existe une infinité de nebulons par le simple fait qu’à des endroits la matière s’est assemblée de la sorte.  Et avec un nombre infini d’Ignorants, le Grand Bang perd son sens. L’impression d’être éteint de toute connaissance m’engloutit, devrais-je renoncer à mon rôle de scribe?  -Androme
""",

    """On croyait en un Créateur puisqu’il donnait un sens à notre origine. On croyait en une Vérité puisqu’elle éclairait notre direction.  Toutefois, dans une nébuleuse infinie, notre origine n’est que statistique et notre direction n’est que passablement statique.  En passant à la deuxième phase, la majorité a choisi le déni.  Mais j’en reviens à me questionner sur l'existence même des autres nebulons. Je pourrais très bien avoir communiqué avec un arrangement aléatoire d’ondes cosmiques depuis le départ.  Je me sens terriblement plus seul que lorsque j’étais Ignorant.  J’envie ma copie qui n’a jamais été contactée.  -Androme
""",

    """Bien qu’il existe certainement des constantes objectives dans la nébuleuse, l’infini empêche une Vérité absolue. Par définition, le vrai devient faux un infini plus loin.  Ma solution: les vérités locales.  La seule vérité que je possède est la mienne, celle que j’ai fondée sur mes expérimentations et les vérités de mes confrères.  Ma vérité croît lorsqu’une de mes questions est répondue.  Toutefois, j’ai la forte intuition que certaines resteront sans réponse.  Ainsi, j'ai choisi que le Créateur existe sous une forme qui ne contredit en rien ma vérité.  Et si vous parvenez à me prouver le contraire, et bien j’apprendrai car ma vérité est malléable.  -Zaurion
""",

    """Maintenant que nous sommes unis, la preuve de l’Intelligent s’avère erronée, les filaments limites semblent se répéter dû à la résonance de nos ondulations.  Nous ne pouvons rien conclure sur la taille de la nébuleuse, mais le concept de vérité locale m’a profondément séduit.  Il nous octroie un véritable pouvoir sur ce qui nous est inatteignable tant que nous cherchons à élargir les frontières de notre savoir.  Mais surtout, elle nous aide à comprendre nos voisins.  En admettant que des parties de nos vérités diffèrent dû à nos vécus, il devient simple d’admirer la complexité et la diversité de chacun.  -Androme
"""
]


