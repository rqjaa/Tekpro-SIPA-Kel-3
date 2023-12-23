#import modul
import pygame
from pygame.locals import *
import random
import os

pygame.init()

#set waktu
jam = pygame.time.Clock()
fps = 60
screen_widht = 864
screen_height = 936

#set display
screen = pygame.display.set_mode((screen_widht, screen_height))
pygame.display.set_caption(('Flap Flap'))

#font
font = pygame.font.SysFont('Bauhaus 93', 60)
font2 = pygame.font.SysFont('Comic Sans', 35)

#warna font
white = (255,255,255)
black = (0,0,0)
navy = (24, 154,180)

#variabel game
lantai_jalan = 0
cepat = 5
terbang = False
game_over = False
pipe_gap = 200
pipe_freq = 1500 #milisekon
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False
SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0


#aset
bg = pygame.image.load('img/background1.png')
lantai = pygame.image.load('img/ground1.jpeg')
tombol_restart = pygame.image.load('img/restart.png')
music = pygame.mixer.music.load('img/music.ogg')
pygame.mixer.music.play(-1)


#text di layar
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img,(x,y))

def reset_game():
    pipe_group.empty()
    flap.rect.x = 100
    flap.rect.y = int(screen_height/2)
    score = 0
    return score


#skin burung
class Bird(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):
            img = pygame.image.load(f'img/bola{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0
        self.clicked = False

    def update(self):
        
        if terbang == True:
        #gravitasi
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            #lompat
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            #animasi
            self.counter +=1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]


            #putar
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)        

class Pipe (pygame.sprite.Sprite):
    def __init__(self,x,y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe1.png')
        self.rect = self.image.get_rect()
       
        # 1 atas -1 bawah
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x,y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= cepat
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        
    def draw(self):

        action = False

        #posisi mouse
        pos = pygame.mouse.get_pos()

        #cek jika mouse di tombol
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #tambah tombol
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flap = Bird(100, int(screen_height/2))

bird_group.add(flap)

#posisi tombol
button =  Button(screen_widht//2 - 50, screen_height // 2 + 50, tombol_restart)

run = True
while run:
    
        jam.tick(fps)

        screen.blit(bg, (0,0))

        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)
        #lantai
        screen.blit(lantai,(lantai_jalan,768))

        #cek skor
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
                pass_pipe = True
            if pass_pipe == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False


        draw_text(str(score), font, white, int(screen_widht/2), 20)

    

        #tabrak pipa dan lagu mati
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flap.rect.top < 0:
            game_over = True
            pygame.mixer.music.pause()
        #burung tabrak lantai dan lagu mati
        if flap.rect.bottom >= 768:
            game_over = True
            terbang = False
            pygame.mixer.music.pause()

        #game over
        if game_over == False and terbang == True:

            #pipa
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_freq:
                pipe_height = random.randint(-130,130)
                btm_pipe = Pipe(screen_widht, int(screen_height/2) + pipe_height, -1)
                top_pipe = Pipe(screen_widht, int(screen_height/2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            #lantai dan lantainya berjalan
            lantai_jalan -= cepat
            if abs(lantai_jalan) > 35:
                lantai_jalan = 0
            pipe_group.update()

        #check game over dan ulang
        if game_over == True:
            pygame.draw.rect(screen, navy, ((int(screen_widht/2-190)), (int(screen_height/2-200)), 400, 400), width=0, border_radius=10)
            #update high score
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
                    #nambahin teks highscore(untuk ubah ganti yg int)
            draw_text('HIGHSCORE :' + str(high_score), font2, white, int(screen_widht/2-135), int(screen_height/2 - 150))
            #teks skor
            draw_text('SCORE :' + str(score), font2, white, int(screen_widht/2-75), int(screen_height/2 - 100))
            if button.draw() == True:
                game_over = False
                score = reset_game()
                pygame.mixer.music.play()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == SONG_END:
                pygame.mixer.music.play()
            if event.type == pygame.MOUSEBUTTONDOWN and terbang == False and game_over == False:
                terbang = True

        pygame.display.update()

pygame.quit()            