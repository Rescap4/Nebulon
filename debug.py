from settings import *
import sys #used in main

pygame.init()
font = pygame.font.Font(None, 30)

def debug(info, y= 10, x= 10):
    display_surf = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    display_surf.blit(debug_surf, debug_rect)