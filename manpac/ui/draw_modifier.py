from manpac.utils import export
from manpac.modifiers.swap_modifier import SwapModifier
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.modifiers.intangible_modifier import IntangibleModifier
from manpac.modifiers.ghost_block_modifier import GhostBlockModifier
from manpac.ui.draw_utils import rect_border

import pygame


def __render_block__(display, image, pos):
    my_rect = rect_border(image.get_width(), image.get_height(), 1, (255, 0, 0))
    display.blit(my_rect, pos)
    return 0


def __blit_alpha__(display, image, pos):
    temp = pygame.Surface((image.get_width(), image.get_height())).convert()
    temp.blit(display, (-pos[0], -pos[1]))
    temp.blit(image, (0, 0))
    temp.set_alpha(126)
    display.blit(temp, pos)
    return 1


__BOOST_SPRITE_LIST__ = [("swap", SwapModifier), ("theghost", IntangibleModifier), ("speed", SpeedModifier), ("diamond", GhostBlockModifier)]
__BOOST_SPRITES__ = None


@export
def init(scale):
    global __BOOST_SPRITES__
    if __BOOST_SPRITES__ is None:
        __BOOST_SPRITES__ = {}
        for (sprite_name, modifierCls) in __BOOST_SPRITE_LIST__:
            boost_image = pygame.image.load("assets/{}.png".format(sprite_name)).convert_alpha()
            __BOOST_SPRITES__[modifierCls] = pygame.transform.scale(boost_image, (scale, scale))


@export
def draw_modifier_icon(display, modifier, nb_boost, number, scale, border=5):
    for modifierCls, sprite in __BOOST_SPRITES__.items():
        if isinstance(modifier, modifierCls):
            display.blit(sprite, (nb_boost * (scale + border), number * scale * 2))


@export
def draw_effect(display, image, pos, modifier_list):
    alpha = 0
    for modifier in modifier_list:
        for (modifierCls, needtodraw) in [[IntangibleModifier, [True, __blit_alpha__]],
                                          [GhostBlockModifier, [True, __render_block__]]]:
            should_draw, drawer = needtodraw
            if isinstance(modifier, modifierCls) and should_draw:
                alpha += drawer(display, image, pos)
                needtodraw[0] = False
    if alpha == 0:
        display.blit(image, pos)
