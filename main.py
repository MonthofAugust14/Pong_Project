import pygame, sys, random


class Block(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center = (x_pos,y_pos))      

class Player(Block):
    def __init__(self, path, x_pos, y_pos, speed):
        super().__init__(path, x_pos, y_pos)
        self.speed = speed
        self.movement = 0
    
    def screen_constrain(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height
    
    def update(self, ball_group):
        self.rect.y += self.movement
        self.screen_constrain()

class Ball(Block):
    def __init__(self, path, x_pos, y_pos, speed_x, speed_y, paddles):
        super().__init__(path, x_pos, y_pos)
        self.speed_x = speed_x * random.choice((-1,1))
        self.speed_y = speed_y * random.choice((-1,1))
        self.paddles = paddles
        self.active = False
        self.score_time = 0

    def update(self):
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.collisions()
        else:
            self.restart_counter()
    
    def collisions(self):
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            pygame.mixer.Sound.play(pong_sound)
            self.speed_y *= -1

        if pygame.sprite.spritecollide(self, self.paddles, False):
            pygame.mixer.Sound.play(pong_sound)
            collision_paddle = pygame.sprite.spritecollide(self,self.paddles, False)[0].rect
            if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x >0:
                self.speed_x *= -1
            if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
                self.speed_x *= -1
            if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y <0:
                self.rect.top = collision_paddle.bottom
                self.speed_y *= -1
            if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
                self.rect.bottom = collision_paddle.top
                self.speed_y *= -1
    
    def reset_ball(self):
        self.active = False
        self.speed_x *= random.choice((-1,1))
        self.speed_y *= random.choice((-1,1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (screen_width/2, screen_height/2)
        pygame.mixer.Sound.play(score_sound)

    def restart_counter(self):
        current_time = pygame.time.get_ticks()
        countdown_number = 3

        if current_time - self.score_time <= 700:
            countdown_number = 3
        if 700 < current_time - self.score_time <= 1400:
            countdown_number = 2
        if 1400 < current_time - self.score_time <= 2100:
            countdown_number = 1
        if current_time - self.score_time >= 2100:
            self.active = True

        time_counter = game_font.render(str(countdown_number), True, accent_color)
        time_counter_rect = time_counter.get_rect(center = (screen_width/2, screen_height/2 +50))
        pygame.draw.rect(window, bg_color, time_counter_rect)
        window.blit(time_counter, time_counter_rect)

class Opponent(Block):
    def __init__(self, path, x_pos, y_pos, speed):
        super().__init__(path, x_pos, y_pos)
        self.speed = speed

    def update(self, ball_group):
        if self.rect.top < ball_group.sprite.rect.y:
            self.rect.y += self.speed
        if self.rect.bottom > ball_group.sprite.rect.y:
            self.rect.y -= self.speed
        self.constrain()

    def constrain(self):
        if self.rect.top <= 0: self.rect.top = 0
        if self.rect.bottom >= screen_height: self.rect.bottom = screen_height

class GameManager:
    def __init__(self, ball_group, paddle_group):
        self.player_score = 0
        self.opponent_score = 0
        self.ball_group = ball_group
        self.paddle_group = paddle_group

    def run_game(self):
        self.paddle_group.draw(window)
        self.ball_group.draw(window)

        self.paddle_group.update(self.ball_group)
        self.ball_group.update()
        self.reset_ball()
        self.draw_score()

    def reset_ball(self):
        if self.ball_group.sprite.rect.right >= screen_width:
            self.opponent_score += 1
            self.ball_group.sprite.reset_ball()
        if self.ball_group.sprite.rect.left <= 0:
            self.player_score += 1
            self.ball_group.sprite.reset_ball()

    def draw_score(self):
        player_score = game_font.render(str(self.player_score), True, accent_color)
        opponent_score = game_font.render(str(self.opponent_score), True, accent_color)

        player_score_rect = player_score.get_rect(midleft = (screen_width/2 + 40, screen_height/2))
        opponent_score_rect = opponent_score.get_rect(midright = (screen_width/2 - 40, screen_height/2))

        window.blit(player_score, player_score_rect)
        window.blit(opponent_score, opponent_score_rect)

class MainMenu():
    def __init__(self, x, y, script, font, color):
        self.script = font.render(script, True, color)
        self.rect = self.script.get_rect(center = (x,y))
        self.clicked = False
    
    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                pygame.mixer.Sound.play(score_sound)
                self.clicked = True
                action = True       
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        window.blit(self.script, self.rect)

        return action
    


#the first 3 vairables are default. Last variable is the buffer size. Changing this fixes the sound delay caused by the buffer time. Make sure the value is not too small, otherwise the sound is bad.
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

#main game window
screen_width = 1280
screen_height = 960
#Create the display window
window = pygame.display.set_mode((screen_width, screen_height))
#Sets the title of the window
pygame.display.set_caption('Pong')

#Global Variables
bg_color = pygame.Color('#2F373F')
accent_color = (27,35,43)
light_grey = (200,200,200)
game_font = pygame.font.Font("freesansbold.ttf", 32)
title_font = pygame.font.Font("freesansbold.ttf", 500)
pong_sound = pygame.mixer.Sound("pong.ogg")
score_sound = pygame.mixer.Sound("score.ogg")
middle_strip = pygame.Rect(screen_width/2-2, 0, 4, screen_height)
menu_screen = True
play_game = False

#Game Objects
player = Player('Paddle.png', screen_width -20, screen_height/2,5)
opponent = Opponent('Paddle.png', 20, screen_width/2,5)
paddle_group = pygame.sprite.Group()
paddle_group.add(player)
paddle_group.add(opponent)
ball = Ball('Ball.png', screen_width/2, screen_height/2,4,4,paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

#Menu Objects
title = MainMenu(screen_width/2, screen_height/2 - 120, "Pong", title_font, light_grey)
start_button = MainMenu(screen_width/2, screen_height/2 + 350, "Start", game_font, light_grey)
exit_button = MainMenu(screen_width/2, screen_height/2 + 400, "Exit", game_font, light_grey)

game_manager = GameManager(ball_sprite, paddle_group)

#Pretty much the "window.Tk() / window.mainloop()"
while menu_screen:
    window.fill(bg_color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    title.draw()
    if start_button.draw():
        menu_screen = False
        play_game = True
    if exit_button.draw():
        pygame.quit()
        sys.exit()

    pygame.display.flip()
    clock.tick(120)

while play_game:
    #input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player.movement += player.speed
            if event.key == pygame.K_UP:
                player.movement -= player.speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.movement -= player.speed
            if event.key == pygame.K_UP:
                player.movement += player.speed


    #Visuals
    #if the background is not filled we would see the prvious frames
    #first code written in drawn on the bottom of the frame, the next is always drawn "on top" of the previous object
    window.fill(bg_color)
    pygame.draw.rect(window, accent_color, middle_strip)

    #class that runs the game
    game_manager.run_game()

    #Updates the window
    pygame.display.flip()
    #Limits how fast the loop runs. If the speed is not controlled, the computer will attempt to run the code as fast as it can.
    clock.tick(120)