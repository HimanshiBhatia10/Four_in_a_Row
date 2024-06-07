import pygame

class button:
    def __init__(self,image,xcord,ycord,scale):
        pic = pygame.image.load(image).convert_alpha()
        height = pic.get_height()
        width = pic.get_width()
        self.image = pygame.transform.scale(pic, (int(width*scale),int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (xcord,ycord)
        self.clicked = False


    def draw(self,surface):
        surface.blit(self.image,(self.rect.topleft))

    def is_clicked(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return action









