import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 480
TITLE = "Meu Platformer"

GRAVITY = 0.6
JUMP_FORCE = 13
MOVE_SPEED = 4

game_state = "menu"  # "menu" ou "playing"
sound_on = True

buttons = {
    "start": Rect(300, 150, 200, 50),
    "sound": Rect(300, 220, 200, 50),
    "exit": Rect(300, 290, 200, 50),
}

platforms = [
    Rect(0, 440, 800, 40),     # chao
    Rect(150, 340, 150, 20),
    Rect(400, 260, 150, 20),
    Rect(620, 180, 150, 20),
]

hero = Rect(50, 300, 32, 32)
velocity_y = 0
on_ground = False

class AnimatedSprite:
    def __init__(self, frames, frame_duration=0.15):
        self.frames = frames
        self.frame_duration = frame_duration
        self.timer = 0
        self.index = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def current_frame(self):
        return self.frames[self.index]

hero_anim = AnimatedSprite(["hero_idle1", "hero_idle2", "hero_idle3", "hero_idle4"], frame_duration=0.2)
hero_walk_anim = AnimatedSprite(["hero_walk1", "hero_walk2", "hero_walk3"], frame_duration=0.15)
moving = False
hero_sprite = Actor("hero_idle1")

class Enemy:
    def __init__(self, x, y, left_limit, right_limit):
        self.rect = Rect(x, y, 32, 32)
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.direction = 1
        self.speed = 2
        self.anim = AnimatedSprite(["enemy_walk1", "enemy_walk2", "enemy_walk3", "enemy_walk4", "enemy_walk5", "enemy_walk6"], frame_duration=0.2)
        self.sprite = Actor("enemy_walk1")

    def update(self, dt):
        self.anim.update(dt)
        self.rect.x += self.speed * self.direction
        if self.rect.right >= self.right_limit or self.rect.left <= self.left_limit:
            self.direction *= -1

    def draw(self):
        self.sprite.image = self.anim.current_frame()
        self.sprite.midbottom = self.rect.midbottom
        self.sprite.draw()



enemies = [Enemy(450, 390, 400, 700)]


def update(dt):
    global game_state
    if game_state == "playing":
        hero_anim.update(dt)
        update_hero()
        for enemy in enemies:
            enemy.update(dt)
            if hero.colliderect(enemy.rect):
                reset_hero()
        if keyboard.escape:
            game_state = "menu"

def draw_button(rect, label):
    screen.draw.filled_rect(rect, "darkslateblue")
    screen.draw.text(label, center=rect.center, fontsize=28, color="white")


def draw():
    screen.fill("skyblue")
    if game_state == "menu":
        screen.draw.text("MEU PLATFORMER", center=(WIDTH // 2, 80), fontsize=60)
        draw_button(buttons["start"], "Comecar o jogo")
        sound_label = "Som: ligado" if sound_on else "Som: desligado"
        draw_button(buttons["sound"], sound_label)
        draw_button(buttons["exit"], "Sair")
    else:
        for platform in platforms:
            screen.draw.filled_rect(platform, "saddlebrown")
        # comentario: trocar este retangulo por sprite animado do heroi
        if moving:
            hero_sprite.image = hero_walk_anim.current_frame()
        else:
            hero_sprite.image = hero_anim.current_frame()
        hero_sprite.midbottom = hero.midbottom
        hero_sprite.draw()
        for enemy in enemies:
            enemy.draw()


def on_mouse_down(pos):
    global game_state, sound_on
    if game_state != "menu":
        return
    if buttons["start"].collidepoint(pos):
        game_state = "playing"
        reset_hero()
    elif buttons["sound"].collidepoint(pos):
        sound_on = not sound_on
        # comentario: ligar/desligar a musica de fundo aqui
    elif buttons["exit"].collidepoint(pos):
        exit()


def reset_hero():
    global velocity_y
    hero.topleft = (50, 300)
    velocity_y = 0


def update_hero():
    global velocity_y, on_ground, moving

    moving = False
    if keyboard.left:
        hero.x -= MOVE_SPEED
        moving = True
    if keyboard.right:
        hero.x += MOVE_SPEED
        moving = True
    hero.x = max(0, min(WIDTH - hero.width, hero.x))

    if (keyboard.space or keyboard.up) and on_ground:
        velocity_y = -JUMP_FORCE

    velocity_y += GRAVITY
    step = round(velocity_y)
    hero.y += step

    on_ground = False
    for platform in platforms:
        landed_from_above = hero.bottom - step <= platform.top
        if hero.colliderect(platform) and step > 0 and landed_from_above:
            hero.bottom = platform.top
            velocity_y = 0
            on_ground = True

    if hero.top > HEIGHT:  # caiu da tela
        reset_hero()


def update(dt):
    global game_state
    if game_state == "playing":
        hero_anim.update(dt)
        update_hero()
        for enemy in enemies:
            enemy.update(dt)
            if hero.colliderect(enemy.rect):
                reset_hero()
        if keyboard.escape:
            game_state = "menu"

pgzrun.go()