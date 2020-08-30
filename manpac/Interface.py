import sys, pygame
from pygame.locals import *

class Interface:

    width, height = 0,0
    screen = 0
    table_size = (0,0)
    scale = 0
    time = 0
    my_pacman = 0
    my_map = 0

    def __init__(self,table_size,entities,map_table):
        pygame.init()
        pygame.display.set_caption('Manpac')
        self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.time = pygame.time.get_ticks()
        self.size = self.screen.get_size()
        scale_x = self.width / table_size[0]
        scale_y = self.height / table_size[1]
        self.scale = int(min(scale_x,scale_y))
        self.my_pacman = self.Pacman(self.screen, self.scale, entity[0])
        self.map = self.Map(self.screen,map_table,table_size,self.scale)

    class Pacman:
        pos_x,pos_y = 0,0
        Sprite_up = []
        Sprite_down = []
        Sprite_left = []
        Sprite_right = []
        Current_sprite = 0
        Sprite_index = 0
        screen = 0
        pixel = 0

        def __init__(self,display,scale, pos):
            s0 = pygame.image.load("sprite/pacman0.png").convert()
            s0 = pygame.transform.scale(s0,(scale,scale))
            s1 = pygame.image.load("sprite/pacmanb1.png").convert()
            s1 = pygame.transform.scale(s1,(scale,scale))
            s2 = pygame.image.load("sprite/pacmanb2.png").convert()
            s2 = pygame.transform.scale(s2,(scale,scale))
            s3 = pygame.image.load("sprite/pacmand1.png").convert()
            s3 = pygame.transform.scale(s3,(scale,scale))
            s4 = pygame.image.load("sprite/pacmand2.png").convert()
            s4 = pygame.transform.scale(s4,(scale,scale))
            s5 = pygame.image.load("sprite/pacmang1.png").convert()
            s5 = pygame.transform.scale(s5,(scale,scale))
            s6 = pygame.image.load("sprite/pacmang2.png").convert()
            s6 = pygame.transform.scale(s6,(scale),scale))
            s7 = pygame.image.load("sprite/pacmanh1.png").convert()
            s7 = pygame.transform.scale(s7,(scale,scale))
            s8 = pygame.image.load("sprite/pacmanh2.png").convert()
            s8 = pygame.transform.scale(s8,(scale,scale))
            self.pixel = scale
            self.Sprite_up = [s0,s8,s7,s8]
            self.Sprite_down = [s0,s2,s1,s2]
            self.Sprite_right = [s0,s3,s4,s3]
            self.Sprite_left = [s0,s6,s5,s6]
            self.screen = display
            self.pos_x = pos[0]*scale
            self.pos_y = pos[1]*scale
            self.screen.blit(self.Sprite_right[1],(self.pos_x,self.pos_y))

        def down(self):
            self.Current_sprite = self.Sprite_down
            self.pos_y += self.pixel

        def up(self):
            self.Current_sprite = self.Sprite_up
            self.pos_y -= self.pixel

        def left(self):
            self.Current_sprite = self.Sprite_left
            self.pos_x += self.pixel

        def right(self):
            self.Current_sprite = self.Sprite_right
            self.pos_x -= self.pixel

        def draw(self):
            self.screen.blit(self.Current_sprite[self.Sprite_index],(self.pos_x,self.pos_y))
            self.Sprite_index += 1
            self.Sprite_index %= 4

    class Map:

        map_table = []
        table_size = (0,0)
        pixel = 0
        screen = 0

        def __init__(self,display,table,size,scale):
            self.screen = display
            self.map_table = table
            self.table_size = size
            self.pixel = scale

        def draw(self):
            for i in range(self.table_size[0]) :
                for j in range(self.table_size[1]):
                    if map_table[i][j] == 1:
                        pygame.draw.rect(self.screen,(0,0,255),(i*self.pixel,j*self.pixel,self.pixel,self.pixel))

    def draw(self):
        self.screen.fill((0,0,0))
        self.my_pacman.draw()
        self.my_map.draw()

    while True:
        for event in pygame.event.get();
            if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        if self.time - pygame.time.get_ticks() >= 500:
            self.draw()
            pygame.display.update()
            self.time = pygame.time.get_ticks()
