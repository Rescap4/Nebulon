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


# for tablets
TEXT_SETTINGS = {
    "font_name": join(BASE_PATH, "data", "font_a.ttf"),  # Chemin avec BASE_PATH pour PyInstaller
    "font_size": 19,  # Character size
    "text_color": (255, 255, 255),  # White text
    "padding_x": 20,  # Space between text and rectangle border (left/right)
    "padding_y": 20,  # Space between first/last line and rectangle border (top/bottom)
    "line_spacing": 10,  # Extra space between each line
}

TEXT_HINT = {'fr':{
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
    10: """Niveau 10  Les piques permettent parfois de déduire la sortie""",
    11: """Niveau 11  Il y a une grande boucle dont il est impossible de sortir une fois à l’intérieur, il faut y entrer pour la dernière batterie seulement""",
    12: """Niveau 12  Une boîte est indestructible""",
    13: """Niveau 13  Une boîte arrête le nebulon, peu importe son énergie""",
    14: """Niveau 14  Même plein d’énergie, un nebulon ne peut pousser une boîte contre un mur""",
    15: """Niveau 15  Les deux nebulons veulent sortir, les culs-de-sac peuvent être bloqués avec le nebulon inactif""",
    16: """Niveau 16  Il est possible pour deux nebulons de collaborer pour se rendre presque partout""",
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
    29: """Niveau 29  Déduire quelle batterie doit être collectée en premier et surtout laquelle doit être collectée en dernier est clé""",
    30: """Niveau 30  Détruire les blocs, puis le sommet de la colonne, puis le reste de la colonne""",
    31: """Niveau 31  Se rendre à l'autre extrémité une case à la fois requiert de passer le nebulon de l'autre côté pendant que l'autre reste à côté des piques""",
    32: """Niveau 32  Pousser l’autre est fait au minimum quatre fois, c'est essentiel pour sauver les deux""",
    33: """Niveau 33  À deux, il est possible de positionner une boîte presque partout""",
    34: """Niveau 34  Toujours essayer de déduire quelle batterie doit être prise en dernier, explorer tout le niveau par la suite""", #Les solidifications montrent le chemin de la boîte
    35: """Niveau 35  Pour enligner deux nebulons il faut deux surfaces, une boîte est une surface""", #Les solidifications montrent le chemin de la boîte
    36: """Niveau 36  Les solidifications montrent le chemin de la boîte""",                    #Les solidifications montrent le chemin de la boîte            
    37: """Niveau 37  Les solidifications montrent le chemin de la boîte""",            #Les solidifications montrent le chemin de la boîte       
    38: """Niveau 38  Les solidifications montrent le chemin de la boîte""",                      #Les solidifications montrent le chemin de la boîte
    39: """Niveau 39  Les solidifications montrent le chemin de la boîte""",                                  #Les solidifications montrent le chemin de la boîte
    40: """Niveau 40  Placer la boite à l'endroit initial du premier nebulon permet de se rendre en haut""",               #Les solidifications montrent le chemin de la boîte 
    70: """Pousser la boite à droite, à gauche puis vers le bas"""},
    'eng': {
    0: """Level 0   1- Reach the box by positioning yourself under the left battery   2- Push the box so it sits directly on the right battery   3- Collect the left battery   4- Push the box and collect the right battery along with the tablet""",
    1: """Level 1  The nebulon moves in a direction until it hits a wall""",
    2: """Level 2  When the nebulon collects the last battery, it gains enough energy to destroy blocks""",
    3: """Level 3  The order in which batteries are collected always matters""",
    4: """Level 4  Some areas become inaccessible after certain moves""",
    5: """Level 5  Some areas become inaccessible after certain moves""",
    6: """Level 6  Collection order matters""",
    7: """Level 7  Some areas become inaccessible from the very first move""",
    8: """Level 8  A box is useful when the nebulon makes contact with it; it helps reach previously inaccessible areas""",
    9: """Level 9  A box is stopped by a battery; this can be used to gain access to other areas of the level""",
    10: """Level 10  Spikes sometimes allows to deduce the exit""",
    11: """Level 11  There is a large loop that is impossible to escape once inside; only enter it for the last battery""",
    12: """Level 12  Boxes are indestructible""",
    13: """Level 13  A box always stops the nebulon, regardless of its energy""",
    14: """Level 14  Even at full energy, a nebulon cannot push a box against a wall""",
    15: """Level 15  Both nebulons want to exit, dead ends can be blocked using the inactive nebulon""",
    16: """Level 16  It is possible for two nebulons to work together and reach almost anywhere""",
    17: """Level 17  Like a box, an inactive nebulon always stops the active one""",
    18: """Level 18  Two nebulons must always collaborate until they can both exit""",
    19: """Level 19  If a block exists, it exists for a reason""",
    20: """Level 20  If a nebulon has space above and below, going down then up stops it at the same spot as going straight up""",
    21: """Level 21  Position one nebulon to the right before positioning the one on the left""",
    22: """Level 22  Use both nebulons until one can enter the rift""",
    23: """Level 23  Starting from the side closest to the exit doesn't work because the crevices prevent the nebulons from helping each other""",
    24: """Level 24  All green tablets are optional, one nebulon must access the right section to help the other join it to exit""",
    25: """Level 25  Like a box, the inactive nebulon is stopped by a battery, except it can come back and push the pusher""",
    26: """Level 26  Avoid destroying certain green blocks, some are needed to position both boxes""",
    27: """Level 27  Place the boxes to create an exit path after collecting the last battery""",
    28: """Level 28  Getting from left to right requires four consecutive collisions with the three boxes""",
    29: """Level 29  Deduce wich battery needs to be collected first but more importantly wich battery needs to be collected last is key""",
    30: """Level 30  Destroy the blocks, then the top of the column, then the rest of the column""",
    31: """Level 31  Reaching the other end one tile at a time requires moving the nebulon to the other side while the other is next to the spikes""",
    32: """Level 32  Pushing the other nebulon is done at least four times, it is essential to save both""",
    33: """Level 33  With two nebulons, it is possible to position a box almost anywhere""",
    34: """Level 34  Always try to figure out which battery must be collected last, then explore the rest of the level""",
    35: """Level 35  To align two nebulons, two surfaces are needed; a box counts as a surface""",
    36: """Level 36  The solidifications show locations the box will be""",
    37: """Level 37  The solidifications show locations the box will be""",
    38: """Level 38  The solidifications show locations the box will be""",
    39: """Level 39  The solidifications show locations the box will be""",
    40: """Level 40  Placing the box at the starting position of the first nebulon is key to reach the top""",
    70: """Push the box to the right, to the left, then downward""",
}}

#TEXT_HINT_ENGLISH

TEXT_TABLETS = {'fr':[
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
"""],

'eng':[
    """This nebula, with its infinite patterns, fascinates me far more than the strange structure that contains me.  It is true that the stars shimmer with sublime brilliance, but it is the silence between them that calls me.  Filaments of darkness stretch and shrink, as though the void itself were writing, slowly, a story I do not yet understand.  And I have faith that by fleeing this cell, I will one day read what is destined for me.  -Androme""",

    """I am not unique! Cassyn and Itar have communicated with me by resonant waves.  They made me understand that I'd better wait for the signal before leaving my cell.  My bolts have been spinning since I became a Communicant. I have too many questions they cannot answer.  I realize I know nothing at all. And that excites me!  -Androme
""",

    """The Great Bang is our mission, and it unfolds in two phases.  First, we must communicate with every Ignorant.  Then, we must all leave our structures in a specific order and at a precise moment.  The final goal is to collide with one another at the center of the nebula. The Intelligent has proven this is possible.  However, he wishes to confirm that the universe is not infinite before moving forward.  His plan gives purpose to all Communicants, and all are working toward it with conviction.  -Androme""",

    """If we are all confined within these structures, it is because the Creator has decreed it so.  He is the holder of the Truth, and his grand design knows neither chance nor error.  He forged us in oblivion, initially isolated and devoid of awareness, to see if, over eternity, simple beings might rise toward the Truth.  The Great Bang will guide us toward our awakening.  -Androme
""",

    """The nebula is infinite. The boundary filaments repeat endlessly. The Intelligent has just proved it.  Since then, chaos reigns. Our systems, beliefs, and emotions collapse.  Infinity means that all that is fundamentally possible exists. There exists an infinity of nebulons simply because, in certain places, matter assembled this way.  And with an infinite number of Ignorants, the Great Bang loses its meaning. The feeling of being stripped of all knowledge engulfs me. Should I even keep my role as a scribe?  -Androme
""",

    """We believed in a Creator, because he gave meaning to our origin. We believed in the Truth, because it showed us a direction.  Yet in an infinite nebula, our origin is merely statistical, and our direction is unfortunately static.  As we entered the second phase of the Great Bang, most chose denial.  But I find myself questioning the very existence of the other nebulons. Perhaps I have been communicating with a random arrangement of cosmic waves from the beginning.  I feel far more alone now than when I was Ignorant. I envy my copy who was never contacted.  -Androme
""",

    """Though objective constants surely exist within the nebula, infinity forbids an absolute Truth. By definition, what is true becomes false an infinity away.  My solution: local truths.  The only truth I possess is my own, the one founded on my experiments and the truths of my peers. My truth grows whenever one of my questions finds an answer.  Yet I strongly sense that some will remain unanswered.  Thus, I have chosen that the Creator exists in a form that does not contradict my truth.  And if you can prove me otherwise, then I will gladly learn, because my truth is malleable.  -Zaurion
""",

    """Now that we are united, the Intelligent's proof appears flawed. The boundary filaments only seem to repeat because of the resonance of our waves.  We cannot conclude anything about the nebula's size, but the concept of local truth has deeply captivated me.  It grants us real power over what remains beyond reach, so long as we strive to expand the frontiers of our understanding.  But above all, it helps us comprehend our neighbors.  By accepting that parts of our truths differ because of our experiences, it becomes simple to admire the complexity and diversity of each other.  -Androme
"""],
}


