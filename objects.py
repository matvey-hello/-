# objects.py — все объекты игры: кнопки, дино, кактус, лужи, дождь
import pygame
import random
import colorsys
# ТЕСТОВЫЕ значения дождя (для релиза вернуть: 800 и 0.2)
RAIN_START = 200
RAIN_CHANCE = 1.0
BLACK = (40, 40, 40)
WHITE = (255, 255, 255)

# --- параметры, которые выставляет главный файл ---
K = 1.0
WIDTH = 960
HEIGHT = 540
GROUND_Y = 480
GRAVITY = 2300
JUMP_SPEED = -900
DINO_PX = 6
CACTUS_PX = 6

def S(v):
    return int(v * K)

# --- Пиксель-арт ---
DINO_BODY = [
    "..............XXXXXX..",
    ".............XXEXXXXX.",
    ".............XXXXXXXX.",
    ".............XXXXXXXX.",
    ".............XXXXXXXX.",
    ".............XXX......",
    "............XXXXXXXXX.",
    "...........XXXXXX.....",
    ".X........XXXXXXX.....",
    ".X.......XXXXXXXXXX...",
    ".XXXXXXXXXXXXXXXX.X...",
    "..XXXXXXXXXXXXXXX.....",
    "...XXXXXXXXXXXXX......",
    "....XXXXXXXXXXX.......",
    ".....XXXXXXXXX........",
    "......XXXXXXX.........",
    ".......XXXXXX.........",
]
LEGS_A = [
    ".......XX..XX.........",
    ".......XX..XX.........",
    ".......XX..XX.........",
    ".......XX..XX.........",
    ".......XXX..XXX.......",
]
LEGS_B = [
    ".......XX..XX.........",
    ".......XX..XX.........",
    ".......XX..XX.........",
    "......XXX..XX.........",
    "...........XXX........",
]
LEGS_C = [
    ".......XX..XX.........",
    ".......XX..XX.........",
    ".......XX..XX.........",
    ".......XX..XXX........",
    ".......XXX............",
]
CACTUS_ROWS = [
    ".....XX.....",
    ".....XX.....",
    ".....XX.....",
    ".XX..XX..XX.",
    ".XX..XX..XX.",
    ".XX.XXXX.XX.",
    ".XXXXXXXXXX.",
    "...XXXXXX...",
    "....XXXX....",
    "....XXXX....",
    "....XXXX....",
    "....XXXX....",
    "....XXXX....",
    "....XXXX....",
    "....XXXX....",
    "...XXXXXX...",
]
LOCK_ROWS = [
    "..XXX..",
    ".X...X.",
    ".X...X.",
    "XXXXXXX",
    "XXXKXXX",
    "XXXKXXX",
    "XXXXXXX",
]
CLOUD_ROWS = [
    "...XXXX...",
    "..XXXXXX..",
    ".XXXXXXXX.",
    "XXXXXXXXXX",
]

def make_surface(rows, palette, px):
    surf = pygame.Surface((len(rows[0]) * px, len(rows) * px), pygame.SRCALPHA)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in palette:
                pygame.draw.rect(surf, palette[ch], (c * px, r * px, px, px))
    return surf

def _rows(frame=0):
    return DINO_BODY + (LEGS_A, LEGS_B, LEGS_C)[frame % 3]

def dino_surface(color, px, frame=0, outline=False, special=None, t=0.0):
    rows = _rows(frame)
    w, h = len(rows[0]), len(rows)

    if special == "rainbow":
        surf = pygame.Surface((w * px, h * px), pygame.SRCALPHA)
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch != ".":
                    hue = ((c + r) / (w + h) + t * 0.5) % 1.0
                    rgb = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
                    col = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                    eye = BLACK if ch == "E" else col
                    pygame.draw.rect(surf, eye, (c * px, r * px, px, px))
        return surf

    if special == "bw":
        surf = pygame.Surface(((w + 2) * px, (h + 2) * px), pygame.SRCALPHA)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for r, row in enumerate(rows):
                    for c, ch in enumerate(row):
                        if ch != ".":
                            pygame.draw.rect(surf, BLACK, ((c + 1 + dx) * px, (r + 1 + dy) * px, px, px))
        mid = w // 2
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch != ".":
                    col = WHITE if c < mid else BLACK
                    eye = BLACK if ch == "E" else col
                    pygame.draw.rect(surf, eye, ((c + 1) * px, (r + 1) * px, px, px))
        return surf
    if special == "richi":
        # Ричи-волнистик: белая голова с полосками, голубое тело, клювик
        surf = pygame.Surface(((w + 2) * px, (h + 2) * px), pygame.SRCALPHA)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for r, row in enumerate(rows):
                    for c, ch in enumerate(row):
                        if ch != ".":
                            pygame.draw.rect(surf, BLACK, ((c + 1 + dx) * px, (r + 1 + dy) * px, px, px))
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch != ".":
                    if ch == "E":
                        col = BLACK                      # глазик
                    elif r < 7:
                        # головка: белая с волнистыми полосками, как у Ричи
                        col = (235, 235, 240) if r % 2 == 0 else (195, 200, 210)
                    elif c < 12 and (r + c) % 2 == 0:
                        col = (150, 160, 175)            # серое крылышко в полоску
                    else:
                        col = (110, 170, 215)            # голубое тельце
                    pygame.draw.rect(surf, col, ((c + 1) * px, (r + 1) * px, px, px))
                    # убираем рот: закрашиваем щель цветом головы
        for c in range(16, 21):
            pygame.draw.rect(surf, (195, 200, 210), ((c + 1) * px, (5 + 1) * px, px, px))
        # оранжевый клювик там, где рот
        for bc, br in ((21, 4), (22, 4), (21, 5), (22, 5)):
            pygame.draw.rect(surf, (240, 160, 60), ((bc + 1) * px, (br + 1) * px, px, px))
        return surf    
    eye = BLACK if outline else WHITE
    if not outline:
        return make_surface(rows, {"X": color, "E": eye}, px)
    surf = pygame.Surface(((w + 2) * px, (h + 2) * px), pygame.SRCALPHA)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for r, row in enumerate(rows):
                for c, ch in enumerate(row):
                    if ch != ".":
                        pygame.draw.rect(surf, BLACK, ((c + 1 + dx) * px, (r + 1 + dy) * px, px, px))
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ".":
                col = eye if ch == "E" else color
                pygame.draw.rect(surf, col, ((c + 1) * px, (r + 1) * px, px, px))
    return surf

cactus_surf = None
lock_surf = None
cloud_surf = None

def configure(k, width, height, ground_y, gravity, jump_speed, dino_px, cactus_px):
    """Главный файл вызывает это при старте и при повороте экрана."""
    global K, WIDTH, HEIGHT, GROUND_Y, GRAVITY, JUMP_SPEED, DINO_PX, CACTUS_PX
    global cactus_surf, lock_surf, cloud_surf
    K = k
    WIDTH = width
    HEIGHT = height
    GROUND_Y = ground_y
    GRAVITY = gravity
    JUMP_SPEED = jump_speed
    DINO_PX = dino_px
    CACTUS_PX = cactus_px
    cactus_surf = make_surface(CACTUS_ROWS, {"X": (60, 140, 60)}, CACTUS_PX)
    lock_surf = make_surface(LOCK_ROWS, {"X": BLACK, "K": WHITE}, max(2, S(30) // 7))
    cloud_surf = make_surface(CLOUD_ROWS, {"X": (130, 130, 140)}, max(2, S(50) // 10))

class Button:
    def __init__(self, text, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect, max(2, S(3)))
        t = self.font.render(self.text, True, BLACK)
        surf.blit(t, (self.rect.centerx - t.get_width() // 2,
                      self.rect.centery - t.get_height() // 2))

    def clicked(self, pos):
        return pos is not None and self.rect.collidepoint(pos)

class Dino:
    def __init__(self, color, outline=False, special=None):
        self.color = color
        self.outline = outline
        self.special = special
        self.frame = 0
        self.t = 0.0
        self.sprite = dino_surface(color, DINO_PX, 0, outline, special, 0.0)
        self.w, self.h = self.sprite.get_size()
        self.x = S(80)
        self.y = GROUND_Y - self.h
        self.vy = 0
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

    def update(self, dt):
        self.vy += GRAVITY * dt
        self.y += self.vy * dt
        if self.y >= GROUND_Y - self.h:
            self.y = GROUND_Y - self.h
            self.vy = 0
            self.on_ground = True
        self.t += dt
        if self.on_ground:
            f = int(self.t * 8) % 3
            if f != self.frame or self.special == "rainbow":
                self.frame = f
                self.sprite = dino_surface(self.color, DINO_PX, f, self.outline, self.special, self.t)

    def hitbox(self):
        return pygame.Rect(int(self.x + self.w * 0.15), int(self.y + self.h * 0.05),
                           int(self.w * 0.7), int(self.h * 0.9))

    def draw(self, surf):
        surf.blit(self.sprite, (self.x, self.y))

class Cactus:
    def __init__(self, speed):
        self.w, self.h = cactus_surf.get_size()
        self.x = WIDTH + S(20)
        self.y = GROUND_Y - self.h
        self.speed = speed

    def update(self, dt):
        self.x -= self.speed * dt

    def hitbox(self):
        return pygame.Rect(int(self.x + self.w * 0.2), int(self.y + S(5)),
                           int(self.w * 0.6), int(self.h - S(5)))

    def draw(self, surf):
        surf.blit(cactus_surf, (self.x, self.y))

class Puddle:
    def __init__(self, speed):
        self.w = S(90)
        self.h = S(12)
        self.x = WIDTH + S(20)
        self.y = GROUND_Y - S(4)
        self.speed = speed

    def update(self, dt):
        self.x -= self.speed * dt

    def hitbox(self):
        return pygame.Rect(int(self.x + S(10)), int(self.y), int(self.w - S(20)), int(self.h))

    def draw(self, surf):
        pygame.draw.ellipse(surf, (90, 150, 230), (self.x, self.y, self.w, self.h))
        pygame.draw.ellipse(surf, (150, 200, 255), (self.x + self.w * 0.2, self.y + S(3),
                                                   self.w * 0.6, self.h - S(6)))

# --- настройки дождя ---
RAIN_FIRST = 700     # первый бросок кубика на 700 м
RAIN_CHANCE = 0.25   # шанс дождя 25%
RAIN_DURATION = 30   # дождь идёт 30 секунд
RAIN_STEP = 100      # не выпало — кубик снова через 100 м
RAIN_AGAIN = 500     # после дождя — следующий шанс через 500 м

class Rain:
    """Погода: ясно → тучи (3 сек) → дождь → ясно. Повторяется бесконечно."""
    def __init__(self):
        self.state = "clear"
        self.timer = 0.0
        self.next_roll = RAIN_FIRST
        self.clouds = []
        self.drops = []

    def _make_clouds(self):
        self.clouds = [[random.uniform(0, WIDTH), S(40) + i * S(50),
                        random.uniform(0.6, 1.2)] for i in range(3)]

    def _make_drops(self):
        self.drops = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT)] for _ in range(40)]

    def _move_clouds(self, dt):
        for cl in self.clouds:
            cl[0] -= S(80) * cl[2] * dt
            if cl[0] < -S(120):
                cl[0] = WIDTH + S(20)

    def update(self, dt, score):
        if self.state == "clear":
            if score >= self.next_roll:
                if random.random() < RAIN_CHANCE:   # бросок кубика
                    self.state = "clouds"
                    self.timer = 3.0
                    self._make_clouds()
                else:
                    self.next_roll += RAIN_STEP     # не выпало — через 100 м снова
        elif self.state == "clouds":
            self.timer -= dt
            self._move_clouds(dt)
            if self.timer <= 0:
                self.state = "rain"
                self.timer = RAIN_DURATION
                self._make_drops()
        else:  # rain
            self.timer -= dt
            self._move_clouds(dt)
            for d in self.drops:
                d[1] += S(1000) * dt
                d[0] -= S(150) * dt
                if d[1] > GROUND_Y:
                    d[1] = -S(20)
                    d[0] = random.uniform(0, WIDTH)
            if self.timer <= 0:
                self.state = "clear"
                self.next_roll = score + RAIN_AGAIN  # после дождя — шанс через 500 м
                self.clouds = []
                self.drops = []

    def raining(self):
        return self.state == "rain"

    def draw(self, surf):
        if self.state in ("clouds", "rain"):
            for cl in self.clouds:
                surf.blit(cloud_surf, (int(cl[0]), int(cl[1])))
        if self.state == "rain":
            for d in self.drops:
                pygame.draw.line(surf, (100, 150, 230), (int(d[0]), int(d[1])),
                                 (int(d[0]) - S(3), int(d[1]) + S(12)), max(2, S(2)))