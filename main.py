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

hero = Rect(50, 380, 30, 50)
velocity_y = 0
on_ground = False


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
        screen.draw.filled_rect(hero, "red")
        # comentario: desenhar os inimigos


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
    hero.topleft = (50, 380)
    velocity_y = 0


def update_hero():
    global velocity_y, on_ground

    if keyboard.left:
        hero.x -= MOVE_SPEED
    if keyboard.right:
        hero.x += MOVE_SPEED
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


def update():
    global game_state
    if game_state == "playing":
        update_hero()
        # comentario: atualizar inimigos e checar colisao com o heroi
        if keyboard.escape:
            game_state = "menu"

pgzrun.go()