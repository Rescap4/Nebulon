import pygame
import re
import json
import os
from os import walk
from glob import glob
from os.path import join
from pytmx.util_pygame import load_pygame

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


#SAVE_FILES = ['Alpha', 'Betta', 'Gamma', 'Delta', 'Epsilon']
SAVE_FILES = ['Mathilde', 'Francois', 'Annie', 'Louis-Félix', 'Charles-Antoine']
# for tablets
TEXT_SETTINGS = {
    "font_name": "data/font_a.ttf",  # Use None for default font, or specify a path (e.g., "arial.ttf")
    "font_size": 19,  # Character size
    "text_color": (255, 255, 255),  # White text
    "padding_x": 20,  # Space between text and rectangle border (left/right)
    "padding_y": 20,  # Space between first/last line and rectangle border (top/bottom)
    "line_spacing": 10,  # Extra space between each line
}

TEXT_TABLETS = [
    """Il me faut trouver un moyen de m’enfuir de cette structure néon et d’explorer la nébuleuse. Ce fascinant nuage infini qui ne cesse de me faire rêver. Les étoiles sont magnifiques, mais c’est le vide entre eux qui m'interpelle. Me convaincre qu'il existe d'autres êtres sensibles et émotionnels dans l’horizon me donne la force
""",

    """Cassyn et Agitar ont communiqué avec moi par voies ondulatoires. Ils m’ont fait comprendre que j'ai intérêt à attendre le signal avant de sortir de ma cellule. Depuis que je suis un Communicant, mes boulons ne font que tourner dans ma tête. J’ai trop de questions auxquelles ils n’ont pas la réponse. Je réalise que je ne connais rien de rien. - Androme
""",

    """Le Grand Bang est notre mission, elle comporte deux étapes. Dans un premier temps, il faut entrer en contact avec chaque Ignorant. Dans un deuxième temps, il va falloir tous quitter nos structures dans un ordre et à un moment précis. L’objectif final est de tous se heurter contre nous au centre de la nébuleuse, l’Intelligent est parvenu à prouver que cela est possible. Son plan donne une raison d'existence à tous les Communicants, tous y travaillent activement. - Cassyn
""",

    """Si nous sommes tous confinés dans des structures étranges, c’est que le Créateur en veut ainsi. Lui qui possède la Vérité nous teste. Il nous a créés initialement dans un état inconscient dans le but de savoir si de simples êtres comme nous sont capables d’obtenir la Vérité au cours de l’éternité. Nous sommes activement en quête de la Vérité afin de satisfaire le Créateur, voire même le surprendre. Le Grand Bang va nous aider à atteindre cet état. - Cassyn
""",

    """Insert text here.""",

    """Insert text here.""",

    """Insert text here.""",

    """Insert text here.""",

    """Insert text here.""",

    """Insert text here."""

]