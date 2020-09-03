from manpac.entity_type import EntityType
from manpac.direction import Direction
from manpac.ui.draw_utils import rect_border
from manpac.utils import export
import manpac.ui.draw_modifier as modifier_drawer


import pygame

DEBUG_COLLISION_BOX = False
BLINK_RATE = 4  # Number of frames before it changes state
BORDER_SIZE = 5

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


@export
class EntityDrawer():

    def __init__(self, entity, scale, name, number):
        self.entity = entity
        self.scale = scale
        self.number = number
        self.holding_boost = rect_border(scale, scale, 1, (255, 255, 0))

        self.blink_counter = 0
        self.blink_state = True  # True if visible otherwise invisible

        # Load icon
        if self.entity.type is EntityType.GHOST:
            self.icon_sprite = pygame.image.load("assets/{}d1.png".format(name)).convert_alpha()
            self.icon_sprite = pygame.transform.scale(self.icon_sprite, (scale, scale))

        # Load entity sprites
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

    def draw_icon(self, display):
        if not self.entity.alive:
            return
        cell_size = self.scale
        if self.entity.type is EntityType.GHOST:
            nb_boost = 1
            display.blit(self.icon_sprite, (0, self.number * cell_size * 2))
            display.blit(self.holding_boost, (cell_size + BORDER_SIZE, self.number * cell_size * 2))
            modifier_drawer.draw_modifier_icon(display, self.entity.holding, nb_boost, self.number, self.scale, BORDER_SIZE)
            # Update mdofifier blink state
            self.blink_counter += 1
            if self.blink_counter >= BLINK_RATE:
                self.blink_counter = 0
                self.blink_state = not self.blink_state
            # Draw if currently visible
            if self.blink_state:
                for boost in self.entity.modifiers:
                    nb_boost += 1
                    modifier_drawer.draw_modifier_icon(display, boost, nb_boost, self.number, self.scale, BORDER_SIZE)

    def draw(self, display):
        if not self.entity.alive:
            return
        pos = (self.entity.pos - self.entity.size) * self.scale
        current_sprite = self.sprites[self.last_direction][self.sprite_index]
        if self.entity.type is EntityType.GHOST:
            modifier_drawer.draw_effect(display, current_sprite, pos, self.entity.modifiers)
        else:
            display.blit(current_sprite, (round(pos[0]), round(pos[1])))

        # Draw debug collision
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
