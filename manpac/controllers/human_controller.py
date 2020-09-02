import pygame
from manpac.utils import export
from manpac.direction import Direction
from manpac.controllers.abstract_controller import AbstractController


@export
class HumanController(AbstractController):
    """
    Reprents the human controller.

    Parameters
    -----------
    - *game*: (**Game**)
        the game this controller is being used in
    - *left*: (**pygame key int**)
        the key that will be used to face left direction
    - *right*: (**pygame key int**)
        the key that will be used to face right direction
    - *down*: (**pygame key int**)
        the key that will be used to face down direction
    - *up*: (**pygame key int**)
        the key that will be used to face up direction
    - *boost*: (**pygame key int**)
        the key that will be used to face boost direction
    """

    def __init__(self, game, left=pygame.K_LEFT, right=pygame.K_RIGHT, down=pygame.K_DOWN, up=pygame.K_UP, boost=pygame.K_SPACE):
        super(HumanController, self).__init__(game)
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.boost = boost

    def update(self, ticks):
        my_direction = None
        #  List all the key and the pressed key are true
        L = pygame.key.get_pressed()
        if L[self.right]:
            my_direction = Direction.RIGHT
        elif L[self.left]:
            my_direction = Direction.LEFT
        elif L[self.up]:
            my_direction = Direction.UP
        elif L[self.down]:
            my_direction = Direction.DOWN

        if L[self.boost]:
            self.entity.use_modifier()
        # Indicate the direction and move if a key is pressed
        if my_direction is not None:
            self.entity.direction = my_direction
            self.entity.moving = True
        else:
            self.entity.moving = False
        self.game.map.move(self.entity, ticks)
