import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 480
LEVEL_WIDTH = 2400
TITLE = "As aventuras do heroi"

GRAVITY = 0.6
JUMP_FORCE = 13
MOVE_SPEED = 4

MAX_LIVES = 3
INVULNERABLE_TIME = 1.5

game_state = "menu"  # "menu" or "playing"
sound_on = True

game_over_buttons = {
    "restart": Rect(300, 220, 200, 50),
    "menu": Rect(300, 290, 200, 50),
}

buttons = {
    "start": Rect(300, 150, 200, 50),
    "sound": Rect(300, 220, 200, 50),
    "exit": Rect(300, 290, 200, 50),
}

platforms = [
    Rect(0, 440, 900, 40),  # ground, first part
    Rect(1020, 440, 1380, 40),  # ground, second part (pit before it)
    Rect(150, 340, 150, 20),
    Rect(400, 260, 150, 20),
    Rect(620, 180, 150, 20),
    Rect(1250, 350, 150, 20),
    Rect(1500, 270, 150, 20),
    Rect(1750, 350, 150, 20),
    Rect(2050, 340, 150, 20),
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

    def current_frame(self, flipped=False):
        name = self.frames[self.index]
        return name + "_left" if flipped else name


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
        self.lives = MAX_LIVES
        self.invulnerable_timer = 0
        self.facing_left = False
        self.prev_bottom = self.rect.bottom

    def reset(self):
        self.rect.topleft = self.start_pos
        self.velocity_y = 0
        self.prev_bottom = self.rect.bottom

    def new_game(self):
        self.lives = MAX_LIVES
        self.invulnerable_timer = 0
        self.reset()

    def take_hit(self):
        if self.invulnerable_timer > 0:
            return
        self.lives -= 1
        self.invulnerable_timer = INVULNERABLE_TIME
        
    def stomps(self, enemy):
        descending = self.rect.bottom > self.prev_bottom
        was_above = self.prev_bottom <= enemy.rect.top
        return descending and was_above

    def bounce(self):
        self.velocity_y = -JUMP_FORCE * 0.6

    def update(self, dt):
        self.prev_bottom = self.rect.bottom
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        self.idle_anim.update(dt)
        self.walk_anim.update(dt)

        self.moving = False
        if keyboard.left:
            self.rect.x -= MOVE_SPEED
            self.moving = True
            self.facing_left = True
        if keyboard.right:
            self.rect.x += MOVE_SPEED
            self.moving = True
            self.facing_left = False
        self.rect.x = max(0, min(LEVEL_WIDTH - self.rect.width, self.rect.x))

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
            touching = self.rect.colliderect(platform)
            if touching and step > 0 and landed_from_above:
                self.rect.bottom = platform.top
                self.velocity_y = 0
                self.on_ground = True

        if self.rect.top > HEIGHT:  # fell off the screen
            self.lives -= 1
            self.reset()

    def draw(self):
        blinking = int(self.invulnerable_timer * 10) % 2
        if self.invulnerable_timer > 0 and blinking:
            return
        if self.moving:
            anim = self.walk_anim
        else:
            anim = self.idle_anim
        self.sprite.image = anim.current_frame(self.facing_left)
        screen_x = self.rect.centerx - camera_x
        self.sprite.midbottom = (screen_x, self.rect.bottom)
        self.sprite.draw()


class Enemy:
    def __init__(self, x, floor_y, left_limit, right_limit):
        self.rect = Rect(x, 0, 32, 32)
        self.rect.bottom = floor_y
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.direction = 1
        self.speed = 2
        self.alive = True
        self.anim = AnimatedSprite(
            ["enemy_walk1", "enemy_walk2", "enemy_walk3"],
            frame_duration=0.2,
        )
        self.sprite = Actor("enemy_walk1")

    def update(self, dt):
        self.anim.update(dt)
        self.rect.x += self.speed * self.direction
        hit_right = self.rect.right >= self.right_limit
        hit_left = self.rect.left <= self.left_limit
        if hit_right or hit_left:
            self.direction *= -1

    def draw(self):
        self.sprite.image = self.anim.current_frame(self.direction < 0)
        screen_x = self.rect.centerx - camera_x
        self.sprite.midbottom = (screen_x, self.rect.bottom)
        self.sprite.draw()


def create_enemies():
    return [
        Enemy(450, 440, 400, 700),  # on the ground
        Enemy(160, 340, 150, 300),  # on the platform at y=340
        Enemy(410, 260, 400, 550),  # on the platform at y=260
        Enemy(1150, 440, 1050, 1300),  # on the ground, second part
        Enemy(1270, 350, 1250, 1400),  # on the platform at y=350
        Enemy(1520, 270, 1500, 1650),  # on the platform at y=270
        Enemy(1900, 440, 1800, 2100),  # on the ground, second part
    ]


enemies = create_enemies()


hero = Hero(50, 300)


camera_x = 0


def update_camera():
    global camera_x
    camera_x = hero.rect.centerx - WIDTH // 2
    camera_x = max(0, min(LEVEL_WIDTH - WIDTH, camera_x))


def draw_button(rect, label):
    screen.draw.filled_rect(rect, "darkslateblue")
    screen.draw.text(label, center=rect.center, fontsize=28, color="white")


def draw_lives():
    for i in range(hero.lives):
        screen.draw.filled_circle((30 + i * 35, 30), 12, "red")


def draw_victory():
    screen.draw.text(
        "VOCE VENCEU!",
        center=(WIDTH // 2, 100),
        fontsize=70,
        color="gold",
    )
    screen.draw.text(
        "Voce derrotou todos os inimigos!",
        center=(WIDTH // 2, 160),
        fontsize=30,
    )
    draw_button(game_over_buttons["restart"], "Jogar de novo")
    draw_button(game_over_buttons["menu"], "Voltar ao menu")

def draw_game_over():
    screen.draw.text(
        "GAME OVER",
        center=(WIDTH // 2, 100),
        fontsize=70,
        color="red",
    )
    draw_button(game_over_buttons["restart"], "Reiniciar")
    draw_button(game_over_buttons["menu"], "Voltar ao menu")


def update(dt):
    global game_state
    if game_state == "playing":
        hero.update(dt)
        update_camera()
        for enemy in enemies:
            enemy.update(dt)
            if not hero.rect.colliderect(enemy.rect):
                continue
            if hero.stomps(enemy):
                enemy.alive = False
                hero.bounce()
            else:
                hero.take_hit()
        enemies[:] = [enemy for enemy in enemies if enemy.alive]
        if hero.lives <= 0:
            music.stop()
            game_state = "game_over"
        elif not enemies:
            music.stop()
            game_state = "victory"
        elif keyboard.escape:
            game_state = "menu"
            music.stop()


def draw():
    screen.fill("skyblue")
    if game_state == "menu":
        screen.draw.text(
            "AS AVENTURAS DO HEROI",
            center=(WIDTH // 2, 80),
            fontsize=60,
        )
        draw_button(buttons["start"], "Comecar o jogo")
        sound_label = "Som: ligado" if sound_on else "Som: desligado"
        draw_button(buttons["sound"], sound_label)
        draw_button(buttons["exit"], "Sair")
    elif game_state == "game_over":
        music.stop()
        draw_game_over()
    elif game_state == "victory":
        draw_victory()
    else:
        for platform in platforms:
            screen.draw.filled_rect(
                platform.move(-camera_x, 0),
                "saddlebrown",
            )
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        draw_lives()
        screen.draw.text(
            f"Inimigos: {len(enemies)}",
            topright=(WIDTH - 20, 15),
            fontsize=30,
        )


def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "menu":
        if buttons["start"].collidepoint(pos):
            start_game()
        elif buttons["sound"].collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.play("background")
            else:
                music.stop()
        elif buttons["exit"].collidepoint(pos):
            exit()
    elif game_state in ("game_over", "victory"):
        if game_over_buttons["restart"].collidepoint(pos):
            start_game()
        elif game_over_buttons["menu"].collidepoint(pos):
            game_state = "menu"


def start_game():
    global game_state, enemies
    game_state = "playing"
    enemies = create_enemies()
    hero.new_game()
    if sound_on:
        music.play("background")
        music.set_volume(0.5)


pgzrun.go()