from manpac.entity_type import EntityType
from manpac.direction import Direction
from manpac.modifiers.abstract_modifier import AbstractModifier
from manpac.modifiers.swap_modifier import SwapModifier
from manpac.modifiers.speed_modifier import SpeedModifier
from manpac.modifiers.intangible_modifier import IntangibleModifier
from manpac.modifiers.ghost_block_modifier import GhostBlockModifier


import pygame

DEBUG_COLLISION_BOX = False


_IMAGE_SET_ = {
    EntityType.GHOST: ["b1", "b2", "d1", "d2", "g1", "g2", "h1", "h2"],
    EntityType.PACMAN: ["0", "b1", "b2", "d1", "d2", "g1", "g2", "h1", "h2"]
}

_COMBINATIONS_SET_ = {
    EntityType.GHOST:  {
        Direction.LEFT: [4, 5, 4, 5],
        Direction.RIGHT: [2, 3, 2, 3],
        Direction.UP: [6, 7, 6, 7],
        Direction.DOWN: [0, 1, 0, 1]
    },
    EntityType.PACMAN: {
        Direction.LEFT: [0, 6, 5, 6],
        Direction.RIGHT: [0, 3, 4, 3],
        Direction.UP: [0, 8, 7, 8],
        Direction.DOWN: [0, 2, 1, 2]
    }
}


class EntityDrawer():

    def __init__(self, entity, scale, name, number, boost_list):
        self.entity = entity
        self.scale = scale
        self.number = number
        self.boost_list = boost_list
        self.blink = True

        if self.entity.type is EntityType.GHOST:
            self.icon_sprite = pygame.image.load("assets/{}d1.png".format(name)).convert_alpha()
            self.icon_sprite = pygame.transform.scale(self.icon_sprite, (scale, scale))

        s = []
        for postfix in _IMAGE_SET_[entity.type]:
            sprite = pygame.image.load("assets/{}{}.png".format(name, postfix)).convert_alpha()
            sprite = pygame.transform.scale(sprite, (int(scale * (2 * entity.size)), int(scale * (2 * entity.size))))
            s.append(sprite)

        self.sprites = {}
        for direction in Direction:
            set = _COMBINATIONS_SET_[entity.type][direction]
            self.sprites[direction] = [s[i] for i in set]

        self.sprite_index = 0
        self.last_direction = entity.direction

    def draw_modifier(self,display,modifier,nb_boost):
        if isinstance(modifier,SpeedModifier):
            display.blit(self.boost_list[2], (nb_boost * self.scale, self.number * self.scale * 2))
        if isinstance(modifier,SwapModifier):
            display.blit(self.boost_list[0], (nb_boost * self.scale, self.number * self.scale * 2))
        if isinstance(modifier,GhostBlockModifier):
            display.blit(self.boost_list[1], (nb_boost * self.scale, self.number * self.scale * 2))
        if isinstance(modifier,IntangibleModifier):
            display.blit(self.boost_list[3], (nb_boost * self.scale, self.number * self.scale * 2))

    def draw_icon(self, display):
        if not self.entity.alive:
            return
        cell_size = self.scale
        if self.entity.type is EntityType.GHOST:
            nb_boost = 1
            display.blit(self.icon_sprite, (0, self.number * cell_size * 2))
            self.draw_modifier(display,self.entity.holding,nb_boost)
            if self.blink:
                for boost in self.entity.modifiers:
                    nb_boost += 1
                    self.draw_modifier(display,boost,nb_boost)



    def draw(self, display):
        if not self.entity.alive:
            return
        pos = (self.entity.pos - self.entity.size) * self.scale
        current_sprite = self.sprites[self.last_direction][self.sprite_index]

        display.blit(current_sprite, (round(pos[0]), round(pos[1])))
        if DEBUG_COLLISION_BOX:
            pos = self.entity.pos
            cell_size = self.scale
            pygame.draw.circle(display, (255, 0, 0),
                               (round(pos[0] * cell_size), round(pos[1] * cell_size)), round(cell_size * self.entity.size))

        if self.entity.direction != self.last_direction:
            self.last_direction = self.entity.direction
        else:
            self.sprite_index += 1
            self.sprite_index %= 4
