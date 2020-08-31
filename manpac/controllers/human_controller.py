import pygame
from manpac.utils import export
from manpac.direction import Direction
from manpac.entity_type import EntityType
from manpac.controllers.abstract_controller import AbstractController

@export
class HumanController(AbstractController):
    """
    Reprents the human controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    """

    def __init__(self,game):
        super(HumanController,self).__init__(game)

    def update(self,ticks):
        my_direction = 0
        #  List all the key and the pressed key are true
        L = pygame.key.get_pressed()
        if L[pygame.K_RIGHT]:
            my_direction = Direction.RIGHT
        if L[pygame.K_LEFT]:
            my_direction = Direction.LEFT
        if L[pygame.K_UP]:
            my_direction = Direction.UP
        if L[pygame.K_DOWN]:
            my_direction = Direction.DOWN
        #Indicate the direction and move if a key is pressed
        if my_direction != 0:
            self.entity.direction = my_direction
            self.entity.moving = True
        else:
            self.entity.moving = False
