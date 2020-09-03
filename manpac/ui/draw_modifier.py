from manpac.modifiers.swap_modifier import SwapModifier
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.modifiers.intangible_modifier import IntangibleModifier
from manpac.modifiers.ghost_block_modifier import GhostBlockModifier
from manpac.ui.draw_utils import *
import pygame
from copy import deepcopy

class DrawModifier:

    def __init__(self,scale):
        self.boost_list = [("swap", SwapModifier), ("theghost", IntangibleModifier), ("speed", SpeedModifier), ("diamond", GhostBlockModifier)]

        self.not_already_draw = [[IntangibleModifier,[True,self.blit_alpha]],[GhostBlockModifier,[True,self.block]]]
        self.boost_dict = {}
        self.scale = scale
        for (sprite_name, modifierCls) in self.boost_list:
            boost_image = pygame.image.load("assets/{}.png".format(sprite_name)).convert_alpha()
            self.boost_dict[modifierCls] = pygame.transform.scale(boost_image, (self.scale, self.scale))

    def draw_modifier(self, display, modifier, nb_boost,number):
        for modifierCls, sprite in self.boost_dict.items():
            if isinstance(modifier, modifierCls):
                display.blit(sprite, (nb_boost * self.scale, number * self.scale * 2))

    def block(self,display,image,pos):
        my_rect = rect_border(image.get_width(), image.get_height(),1,(255,255,0))
        display.blit(my_rect,pos)
        return 0

    def blit_alpha(self, display, image, pos, ):
        temp = pygame.Surface((image.get_width(), image.get_height())).convert()
        temp.blit(display, (-pos[0], -pos[1]))
        temp.blit(image, (0, 0))
        temp.set_alpha(126)
        display.blit(temp, pos)
        return 1

    def draw_effect(self, display, image, pos, modifier_list):
        alpha = 0
        my_list = deepcopy(self.not_already_draw)
        for modifier in modifier_list:
            for (modifierCls,needtodraw) in my_list:
                if isinstance(modifier,modifierCls) and needtodraw[0]:
                    alpha += needtodraw[1](display,image,pos)
                    needtodraw[0] = False
        if alpha == 0:
            display.blit(image,pos)
