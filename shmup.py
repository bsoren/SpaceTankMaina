# Shmup game
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
import sys

import pygame
import os
import random

# game option/settings
WIDTH = 400
HEIGHT = 600
FPS = 60

# Setup Assets
# img_dir = os.path.join(os.path.dirname(__file__), 'assets', 'img')
# sound_dir = os.path.join(os.path.dirname(__file__), 'assets', 'snd')

img_dir = os.path.join('assets', 'img')
sound_dir = os.path.join('assets', 'snd')

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('comicsans')


# Draw Text on the Screen
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


# Create new mob (Meteor)
def newmob():
    m = Mob()
    all_sprites.add(m)
    mob.add(m)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_game_over_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Arrow keys to move, Space to fire", 22, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press any key to begin...", 18, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evt.type == pygame.KEYUP:
                waiting = False


class Player(pygame.sprite.Sprite):
    # sprite for the Player
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        # self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .80 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_time = pygame.time.get_ticks()
        self.hidden = False
        self.lives = 3
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()
        self.is_powerup = False

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            self.rect.centerx = WIDTH // 2
            self.rect.bottom = HEIGHT - 10

        if self.power >= 2 and pygame.time.get_ticks() - self.power_timer > 6000:
            self.power = 1
            self.power_timer = pygame.time.get_ticks()
            power_down_sound.play()

        self.speedx = 0
        key_state = pygame.key.get_pressed()
        if key_state[pygame.K_LEFT]:
            self.speedx -= 5
        if key_state[pygame.K_RIGHT]:
            self.speedx += 5
        if key_state[pygame.K_SPACE]:
            self.shoot()
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        self.rect.x += self.speedx

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_time > 100:
            self.last_time = now
            if self.power == 1:
                b = Bullet(self.rect.centerx, self.rect.top)
                bullets.add(b)
                all_sprites.add(b)
                shoot_sound.play()
            elif self.power >= 2:
                b1 = Bullet(self.rect.left, self.rect.centery)
                bullets.add(b1)
                all_sprites.add(b1)

                b2 = Bullet(self.rect.right, self.rect.centery)
                bullets.add(b2)
                all_sprites.add(b2)
                shoot_sound.play()

    def powerup(self):
        self.power = 2
        self.power_timer = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH // 2, HEIGHT + 300)


class Mob(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.Surface((30, 30))
        # self.image.fill(RED)
        # self.image_orig = pygame.transform.scale(meteor_img, (50, 40))
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(3, 5)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(3, 10)
            self.speedx = random.randrange(-3, 3)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        # self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Pow(pygame.sprite.Sprite):

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.frame = 0
        self.image = explosion_anim[size][self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame_rate = 75
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now

            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


# Load all game graphics
background = pygame.image.load(os.path.join(img_dir, 'space_bg.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_dir, 'playerShip1_green.png')).convert()
player_img_mini = pygame.transform.scale(player_img, (25, 19))
bullet_img = pygame.image.load(os.path.join(img_dir, 'laserRed07.png')).convert()
meteor_list = ['meteorBrown_big1.png', 'meteorBrown_big2.png', 'meteorBrown_big3.png',
               'meteorBrown_big4.png', 'meteorBrown_med1.png', 'meteorBrown_med3.png',
               'meteorBrown_small1.png', 'meteorBrown_small2.png']
meteor_images = []
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_dir, img)).convert())

explosion_anim = {'lg': [], 'sm': [], 'player': []}
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    # player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey('BLACK')
    explosion_anim['player'].append(img)

powerup_images = {'shield': pygame.image.load(os.path.join(img_dir, 'shield_gold.png')).convert(),
                  'gun': pygame.image.load(os.path.join(img_dir, 'bolt_gold.png')).convert()}

# Load all game sounds
shoot_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'pew.wav'))
shield_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'pow4.wav'))
power_up_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'pow5.wav'))
power_down_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'sfx_shieldDown.ogg'))
explosion_sound_list = ['expl3.wav', 'expl6.wav']
explosion_sounds = []
for sound in explosion_sound_list:
    explosion_sounds.append(pygame.mixer.Sound(os.path.join(sound_dir, sound)))
player_die_sound = pygame.mixer.Sound(os.path.join(sound_dir, 'rumble1.ogg'))
pygame.mixer.music.load(os.path.join(sound_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(loops=-1)

# Game loop
game_over = True
running = True
while running:
    # clock speed
    clock.tick(FPS)
    if game_over:
        show_game_over_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mob = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0

    # process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # update
    all_sprites.update()

    # Check bullets hitting mobs
    hits = pygame.sprite.groupcollide(mob, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius

        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)

        explosion = Explosion(hit.rect.center, 'lg')
        all_sprites.add(explosion)
        explosion_sound = random.choice(explosion_sounds)
        explosion_sound.play()
        newmob()

    #  Check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mob, True, pygame.sprite.collide_circle)
    for hit in hits:
        newmob()
        player.shield -= hit.radius * 2
        explosion = Explosion(hit.rect.center, 'sm')
        all_sprites.add(explosion)
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player_die_sound.play()
            player.hide()
            player.lives -= 1
            player.shield = 100

    # Powerups
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(20, 30)
            shield_sound.play()
            if player.shield > 100:
                player.shield = 100
        if hit.type == 'gun':
            power_up_sound.play()
            player.powerup()

    # if the player died and the explosion has finished playing
    if player.lives <= 0 and not death_explosion.alive():
        game_over = True

    # display/render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_img_mini)

    # flip
    pygame.display.flip()
