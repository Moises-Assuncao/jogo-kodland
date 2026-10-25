import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 480
TITLE = "As aventuras do heroi"

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


class Hero:
    def __init__(self, x, y):
        self.start_pos = (x, y)
        self.rect = Rect(x, y, 32, 32)
        self.velocity_y = 0
        self.on_ground = False
        self.moving = False
        self.idle_anim = AnimatedSprite(
            ["hero_idle1", "hero_idle2", "hero_idle3", "hero_idle4"],
            frame_duration=0.2,
        )
        self.walk_anim = AnimatedSprite(
            ["hero_walk1", "hero_walk2", "hero_walk3"],
            frame_duration=0.15,
        )
        self.sprite = Actor("hero_idle1")

    def reset(self):
        self.rect.topleft = self.start_pos
        self.velocity_y = 0

    def update(self, dt):
        self.idle_anim.update(dt)
        self.walk_anim.update(dt)

        self.moving = False
        if keyboard.left:
            self.rect.x -= MOVE_SPEED
            self.moving = True
        if keyboard.right:
            self.rect.x += MOVE_SPEED
            self.moving = True
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        if (keyboard.space or keyboard.up) and self.on_ground:
            self.velocity_y = -JUMP_FORCE
            if sound_on:
                sounds.jump.play()

        self.velocity_y += GRAVITY
        step = round(self.velocity_y)
        self.rect.y += step

        self.on_ground = False
        for platform in platforms:
            landed_from_above = self.rect.bottom - step <= platform.top
            if self.rect.colliderect(platform) and step > 0 and landed_from_above:
                self.rect.bottom = platform.top
                self.velocity_y = 0
                self.on_ground = True

        if self.rect.top > HEIGHT:
            self.reset()

    def draw(self):
        if self.moving:
            self.sprite.image = self.walk_anim.current_frame()
        else:
            self.sprite.image = self.idle_anim.current_frame()
        self.sprite.midbottom = self.rect.midbottom
        self.sprite.draw()


class Enemy:
    def __init__(self, x, floor_y, left_limit, right_limit):
        self.rect = Rect(x, 0, 32, 32)
        self.rect.bottom = floor_y
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.direction = 1
        self.speed = 2
        self.anim = AnimatedSprite(["enemy_walk1", "enemy_walk2", "enemy_walk3"], frame_duration=0.2)
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


enemies = [
    Enemy(450, 440, 400, 700),   # no chao
    Enemy(160, 340, 150, 300),   # na plataforma de y=340
    Enemy(410, 260, 400, 550),   # na plataforma de y=260
]


hero = Hero(50, 300)


def draw_button(rect, label):
    screen.draw.filled_rect(rect, "darkslateblue")
    screen.draw.text(label, center=rect.center, fontsize=28, color="white")


def update(dt):
    global game_state
    if game_state == "playing":
        hero.update(dt)
        for enemy in enemies:
            enemy.update(dt)
            if hero.rect.colliderect(enemy.rect):
                hero.reset()
        if keyboard.escape:
            game_state = "menu"


def draw():
    screen.fill("skyblue")
    if game_state == "menu":
        screen.draw.text("AS AVENTURAS DO HEROI", center=(WIDTH // 2, 80), fontsize=60)
        draw_button(buttons["start"], "Comecar o jogo")
        sound_label = "Som: ligado" if sound_on else "Som: desligado"
        draw_button(buttons["sound"], sound_label)
        draw_button(buttons["exit"], "Sair")
    else:
        for platform in platforms:
            screen.draw.filled_rect(platform, "saddlebrown")
        hero.draw()
        for enemy in enemies:
            enemy.draw()


def on_mouse_down(pos):
    global game_state, sound_on
    if game_state != "menu":
        return
    if buttons["start"].collidepoint(pos):
        game_state = "playing"
        hero.reset()
        if sound_on:
            music.play("background")
            music.set_volume(0.5)
    elif buttons["sound"].collidepoint(pos):
        sound_on = not sound_on
        if sound_on:
            music.play("background")
        else:
            music.stop()
    elif buttons["exit"].collidepoint(pos):
        exit()

pgzrun.go()