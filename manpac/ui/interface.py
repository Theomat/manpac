import sys
import pygame
from pygame.locals import QUIT

from manpac.cell import Cell
from manpac.game_status import GameStatus
from manpac.entity_type import EntityType
from manpac.ui.entity_drawer import EntityDrawer


class Interface():

    width, height = 0, 0
    screen = 0
    table_size = (0, 0)
    scale = 0
    time = 0
    my_pacman = 0
    my_map = 0

    def __init__(self, game):
        self.game = game
        pygame.init()
        pygame.display.set_caption('Manpac')
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.time = pygame.time.get_ticks()
        self.size = self.screen.get_size()

    def _draw_map_(self):
        for i in range(self.game.map.width):
            for j in range(self.game.map.height):
                if self.game.map[i, j] == Cell.WALL:
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (i*self.scale, j*self.scale, self.scale, self.scale))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_map_()
        for entity_drawer in self.entities_drawer:
            entity_drawer.draw(self.screen)

    def start(self, map):
        self.game.start(map)
        scale_x = self.width / map.width
        scale_y = self.height / map.height
        self.scale = int(min(scale_x, scale_y))

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

        while self.game.status is GameStatus.ONGOING:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

            dt = self.time - pygame.time.get_ticks()
            if dt >= 17:
                self.game.update(dt / 17.)
                self.draw()
                pygame.display.update()
                self.time = pygame.time.get_ticks()
