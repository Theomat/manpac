import sys
import pygame
from pygame.locals import QUIT
import time

from manpac.utils import export
from manpac.cell import Cell
from manpac.game_status import GameStatus
from manpac.entity_type import EntityType
from manpac.ui.entity_drawer import EntityDrawer
import manpac.ui.draw_modifier as modifier_drawer


REFRESH_DELAY = 25


@export
class Interface():

    def __init__(self, game):
        self.game = game
        self.scale = 0

    def _draw_map_(self):
        cell_size = self.scale
        for i in range(self.game.map.width):
            for j in range(self.game.map.height):
                cell = self.game.map[i, j]
                if cell == Cell.WALL:
                    pygame.draw.rect(self.screen, (0, 0, 255),
                                     (i*cell_size, j*cell_size, cell_size, cell_size))
                elif cell == Cell.DEBUG:
                    pygame.draw.rect(self.screen, (255, 0, 0),
                                     (i*cell_size, j*cell_size, cell_size, cell_size))
                elif cell == Cell.DEBUG_ONCE:
                    pygame.draw.rect(self.screen, (0, 255, 0),
                                     (i*cell_size, j*cell_size, cell_size, cell_size))
                    self.game.map[i, j] = Cell.EMPTY

    def draw_boost(self):
        for loc, duration in self.map.ghost_boosts:
            self.screen.blit(self.ghost_boost,
                             (loc[0]*self.scale, loc[1]*self.scale))
        for loc, duration in self.map.pacman_boosts:
            self.screen.blit(self.pacman_boost,
                             (loc[0]*self.scale, loc[1]*self.scale))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self._draw_map_()
        self.draw_boost()
        for entity_drawer in self.entities_drawer:
            entity_drawer.draw(self.screen)
        copy = self.screen.copy()
        self.screen.fill((0, 0, 0))
        self.screen.blit(copy, (self.tx, self.ty))
        for entity_drawer in self.entities_drawer:
            entity_drawer.draw_icon(self.screen)

    def __pygame_init__(self, map):
        pygame.init()
        pygame.display.set_caption('Manpac')
        self.screen = pygame.display.set_mode((900, 600))
        self.width, self.height = self.screen.get_size()
        scale_x = self.width / map.width
        scale_y = self.height / map.height
        self.scale = max(1, round(min(scale_x, scale_y)))

        modifier_drawer.init(self.scale)
        # Compute translation offsets
        self.tx = (self.width - self.scale * map.width) // 2
        self.ty = (self.height - self.scale * map.height) // 2
        self.map = map
        if map.boost_generator:
            self.ghost_boost = pygame.image.load("assets/interro.png").convert_alpha()
            self.ghost_boost = pygame.transform.scale(self.ghost_boost, (self.scale, self.scale))
            self.pacman_boost = pygame.image.load("assets/excla.png").convert_alpha()
            self.pacman_boost = pygame.transform.scale(self.pacman_boost, (self.scale, self.scale))

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
            drawer = EntityDrawer(entity, self.scale, name, ghost)
            self.entities_drawer.append(drawer)

        while self.game.status is GameStatus.NOT_STARTED:
            time.sleep(REFRESH_DELAY)
            self.draw()
            pygame.display.update()

        # Loop
        self.last_updated = pygame.time.get_ticks()
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
