from manpac.entity_type import EntityType
from manpac.direction import Direction

import pygame


_IMAGE_SET_ = {
    EntityType.GHOST: ["b1", "b2", "d1", "d2", "g1", "h1", "h2"],
    EntityType.PACMAN: ["0", "b1", "b2", "d1", "d2", "g1", "h1", "h2"]
}

_COMBINATIONS_SET_ = {
    EntityType.GHOST:  {
        Direction.LEFT: [],
        Direction.RIGHT: [],
        Direction.UP: [],
        Direction.DOWN: []
    },
    EntityType.PACMAN: {
        Direction.LEFT: [0, 6, 5, 6],
        Direction.RIGHT: [0, 3, 4, 3],
        Direction.UP: [0, 8, 7, 8],
        Direction.DOWN: [0, 2, 1, 2]
    }
}


class EntityDrawer():

    def __init__(self, entity, scale, name):
        self.entity = entity
        self.scale = scale

        s = []
        for postfix in _IMAGE_SET_[entity.type]:
            sprite = pygame.image.load("assets/{}{}.png".format(name, postfix)).convert()
            sprite = pygame.transform.scale(sprite, (scale, scale))
            s.append(sprite)

        self.sprites = {}
        for direction in Direction:
            set = _COMBINATIONS_SET_[entity.type][direction]
            self.sprites[direction] = [s[i] for i in set]

        self.sprite_index = 0
        self.last_direction = entity.direction

    def draw(self, display):
        pos = (self.entity.pos - self.entity.size) * self.scale
        current_sprite = self.sprites[self.last_direction][self.sprite_index]
        display.blit(current_sprite, (int(pos[0]), int(pos[1])))

        if self.entity.direction != self.last_direction:
            self.last_direction = self.entity.direction
        else:
            self.sprite_index += 1
            self.sprite_index %= 4
