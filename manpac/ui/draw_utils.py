from manpac.utils.export_decorator import export


import pygame


@export
def rect_border(width, height, border, color):
    """
    Create a rectangle border surface than can now be blit.

    Parameters
    -----------
    - *width*: (**int**)
        the width of the rectangle, border not included
    - *height*: (**int**)
        the height of the rectangle, border not included
    - *border*: (**int**)
        the size of the border in pixels
    - *color*: (**int 3-tuple**)
        the color used to stroke the border
    """
    surf = pygame.Surface((width + border * 2, height + border * 2), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (border, border, width, height), border)
    return surf
