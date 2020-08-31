import sys
import pygame
from pygame.locals import QUIT

from manpac.cell import Cell
from manpac.game_status import GameStatus
from manpac.entity_type import EntityType
from manpac.ui.entity_drawer import EntityDrawer


REFRESH_DELAY = 25


class Interface():

    def __init__(self, game):
        self.game = game
        self.scale = 0

    def _draw_map_(self):
        cell_size = self.scale
        for i in range(self.game.map.width):
            for j in range(self.game.map.height):
                if self.game.map[i, j] == Cell.WALL:
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (i*cell_size, j*cell_size, cell_size, cell_size))
                elif self.game.map[i, j] == Cell.DEBUG:
                    pygame.draw.rect(self.screen, (255, 0, 0),
                                     (i*cell_size, j*cell_size, cell_size, cell_size))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_map_()
        for entity_drawer in self.entities_drawer:
            entity_drawer.draw(self.screen)

    def __pygame_init__(self, map):
        pygame.init()
        pygame.display.set_caption('Manpac')
        self.screen = pygame.display.set_mode((1600, 900))
        self.last_updated = pygame.time.get_ticks()
        self.width, self.height = self.screen.get_size()

        scale_x = self.width / map.width
        scale_y = self.height / map.height
        self.scale = max(1, round(min(scale_x, scale_y)))

    def start(self, map):
        self.__pygame_init__(map)
        self.game.start(map)

        # Create entity drawer
        self.entities_drawer = []
        ghost = 1
        for entity in self.game.entities:
            if entity.type is EntityType.PACMAN:
                name = "pacman"
            else:
                name = "ghost{}".format(ghost)
                ghost += 1
            drawer = EntityDrawer(entity, self.scale, name)
            self.entities_drawer.append(drawer)

        # Loop
        while self.game.status is GameStatus.ONGOING:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            dt = pygame.time.get_ticks() - self.last_updated
            if dt >= REFRESH_DELAY:
                self.game.update(dt / REFRESH_DELAY)
                self.draw()
                pygame.display.update()
                self.last_updated = pygame.time.get_ticks()
