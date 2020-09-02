from manpac.utils.export_decorator import export


import pygame


@export
def rect_border(width, height, border, color, fill_color=(0, 0, 0)):
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
    - *fill_color*: (**int 3-tuple**)
        the color used to fill the inside of the rectangle
    """
    surf = pygame.Surface((width + border * 2, height + border * 2), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, width + border * 2, height + border * 2), 1)
    pygame.draw.rect(surf, fill_color, (border, border, width, height), 0)
    return surf
