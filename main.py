import pygame
import random
import os
import sys

import objects as ob

# --- Настройки ---
FPS = 60
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)
COIN_COLOR = (232, 196, 0)

pygame.init()
try:
    pygame.key.stop_text_input()
except Exception:
    pass

try:
    import sounds
except Exception:
    sounds = None
if sounds:
    sounds.init()

K = 1.0
def S(v):
    return int(v * K)

# имя, цвет, цена, обводка, спец-эффект
SKINS = [
    ("Классик", (53, 53, 53), 0, False, None),
    ("Красный", (217, 48, 48), 5, False, None),
    ("Жёлтый", (232, 196, 0), 10, False, None),
    ("Розовый", (244, 114, 182), 15, False, None),
    ("Голубой", (100, 180, 240), 20, False, None),
    ("Оранжевый", (245, 130, 30), 25, False, None),
    ("Белый", (255, 255, 255), 30, True, None),
    ("Зелёный", (40, 160, 60), 35, False, None),
    ("Синий", (30, 90, 200), 40, False, None),
    ("Фиолетовый", (150, 60, 200), 45, False, None),
    ("Бирюзовый", (0, 180, 180), 50, False, None),
    ("Лаймовый", (180, 230, 30), 55, False, None),
    ("Коралловый", (255, 127, 80), 60, False, None),
    ("Персиковый", (255, 195, 140), 65, False, None),
    ("Индиго", (80, 20, 160), 70, False, None),
    ("Серебряный", (200, 200, 210), 75, True, None),
    ("Чёрно-белый", (0, 0, 0), 80, False, "bw"),
    ("Ричи", (110, 130, 165), 100, False, "richi"),
    ("Радужный", (255, 255, 255), 150, False, "rainbow"),
]
PAGES = [list(range(0, 8)), list(range(8, 16)), list(range(16, 19))]
MAX_PAGE = len(PAGES) - 1

FACTS = [
    "Игру «Динозаврик» создал 11-летний создатель вместе с ИИ Qwen 3.8 Max (по-английски — Qwen3-Max).",
    "Бегущий динозаврик впервые появился в браузере Google Chrome в 2014 году — он бежит, когда нет интернета.",
    "Ричи — настоящий волнистый попугай создателя! Он сине-серый, спокойный и совсем не кусается.",
    "Все звуки игры генерируются кодом на лету — в игре нет ни одного аудиофайла!",
    "Спрайт динозавра нарисован кодом, пиксель за пикселем, без единой картинки.",
    "Радужный скин — самый дорогой (150 монет), потому что переливается всеми цветами радуги.",
    "Дождь в игре идёт 30 секунд, а шанс его появления — 25% после 700 метров.",
    "У настоящего тираннозавра были крошечные лапки — почти как у нашего динозаврика!",
    "Волнистые попугаи, как Ричи, могут выучить почти сотню слов и говорить их.",
    "Вся игра написана на Python с библиотекой pygame и работает прямо на телефоне.",
    "Первый скин в игре — Классик, он бесплатный и открыт с самого начала.",
    "За каждые 200 метров забега дают 1 монетку, а за каждые 1000 метров — сразу 5!",
    "Во время дождя кактусы не растут — вместо них по земле бегут лужи.",
    "Перед дождём всегда плывут тучи — это предупреждение, что через 3 секунды польёт!",
    "У динозаврика есть глаз и пасть — всё нарисовано пикселями прямо в коде.",
    "Белый скин получил чёрную обводку, чтобы не сливаться с белым фоном.",
    "Рекорд, монеты, скины и собранные факты сохраняются в файл save.txt.",
    "Игра сама понимает поворот телефона и подстраивает все размеры под экран.",
    "Волнистые попугаи в дикой природе живут только в Австралии.",
    "Настоящий тираннозавр был длиной с автобус и весил почти как слон!",
]

def _save_dir():
    try:
        from jnius import autoclass
        ctx = autoclass('org.kivy.android.PythonActivity').mActivity
        return ctx.getExternalFilesDir(None).getAbsolutePath()
    except Exception:
        return os.path.dirname(os.path.abspath(__file__))

SAVE_PATH = os.path.join(_save_dir(), "save.txt")
def load_save():
    coins, owned, sel, best, facts = 0, {0}, 0, 0, set()
    try:
        with open(SAVE_PATH) as f:
            for line in f:
                k, _, v = line.strip().partition("=")
                if k == "coins":
                    coins = int(v)
                elif k == "owned":
                    owned = {int(x) for x in v.split(",") if x}
                elif k == "selected":
                    sel = int(v)
                elif k == "best":
                    best = int(v)
                elif k == "facts":
                    facts = {int(x) for x in v.split(",") if x}
    except Exception:
        pass
    if sel not in owned:
        sel = 0
    return coins, owned, sel, best, facts

def save_game():
    try:
        with open(SAVE_PATH, "w") as f:
            f.write(f"coins={coins}\n")
            f.write("owned=" + ",".join(map(str, sorted(owned))) + "\n")
            f.write(f"selected={selected}\n")
            f.write(f"best={best}\n")
            f.write("facts=" + ",".join(map(str, sorted(facts_seen))) + "\n")
    except Exception:
        pass

coins, owned, selected, best, facts_seen = load_save()

def skin_args():
    _, color, _, outline, special = SKINS[selected]
    return color, outline, special

def wrap(text, max_w, font):
    """Разбивает текст на строки, чтобы влезал по ширине."""
    lines = []
    cur = ""
    for word in text.split():
        t = cur + " " + word if cur else word
        if font.size(t)[0] <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def build():
    global screen, WIDTH, HEIGHT, K, GROUND_Y
    global FONT_TITLE, FONT_BTN, FONT_BTN_S, FONT_TEXT, FONT_SMALL
    global BTN_PLAY, BTN_SKINS, BTN_BACK, BTN_BACK_S, BTN_AGAIN, BTN_MENU, BTN_CREDS
    global BTN_NEXT, BTN_PREV, BTN_EXIT, BTN_YES, BTN_NO, BTN_FACTS, BTN_FACT
    screen = pygame.display.set_mode((0, 0))
    try:
        pygame.key.stop_text_input()   # страховка: клавиатура не нужна
    except Exception:
        pass
    WIDTH, HEIGHT = screen.get_size()
    WIDTH, HEIGHT = screen.get_size()
    if WIDTH < 200 or HEIGHT < 200:
        WIDTH, HEIGHT = 960, 540
    K = HEIGHT / 540
    GROUND_Y = HEIGHT - S(60)
    ob.configure(K, WIDTH, HEIGHT, GROUND_Y, S(2300), -S(900),
                 max(2, S(80) // 24), max(2, S(75) // 16))
    FONT_TITLE = pygame.font.SysFont(None, S(96), True)
    FONT_BTN = pygame.font.SysFont(None, S(54), True)
    FONT_BTN_S = pygame.font.SysFont(None, S(40), True)
    FONT_TEXT = pygame.font.SysFont(None, S(44))
    FONT_SMALL = pygame.font.SysFont(None, S(32))
    BTN_PLAY = ob.Button("ИГРАТЬ", WIDTH // 2 - S(130), S(275), S(260), S(65), FONT_BTN)
    BTN_SKINS = ob.Button("СКИНЫ", WIDTH // 2 - S(130), S(345), S(260), S(65), FONT_BTN)
    BTN_CREDS = ob.Button("СОЗДАТЕЛИ", WIDTH // 2 - S(160), S(415), S(320), S(65), FONT_BTN)
    BTN_BACK = ob.Button("НАЗАД", WIDTH // 2 - S(120), HEIGHT - S(110), S(240), S(70), FONT_BTN)
    BTN_BACK_S = ob.Button("НАЗАД", S(20), S(25), S(170), S(60), FONT_BTN_S)
    BTN_NEXT = ob.Button(">", WIDTH - S(90), HEIGHT // 2 - S(35), S(70), S(70), FONT_BTN)
    BTN_PREV = ob.Button("<", S(20), HEIGHT // 2 - S(35), S(70), S(70), FONT_BTN)
    BTN_AGAIN = ob.Button("ЗАНОВО", WIDTH // 2 - S(270), int(HEIGHT * 0.68), S(240), S(70), FONT_BTN)
    BTN_MENU = ob.Button("В МЕНЮ", WIDTH // 2 + S(30), int(HEIGHT * 0.68), S(240), S(70), FONT_BTN)
    BTN_EXIT = ob.Button("НАЗАД", S(20), S(15), S(150), S(50), FONT_BTN_S)
    BTN_YES = ob.Button("ДА", WIDTH // 2 + S(30), int(HEIGHT * 0.55), S(150), S(60), FONT_BTN)
    BTN_NO = ob.Button("НЕТ", WIDTH // 2 - S(180), int(HEIGHT * 0.55), S(150), S(60), FONT_BTN)
    BTN_FACTS = ob.Button("ФАКТЫ", S(20), S(15), S(150), S(50), FONT_BTN_S)
    BTN_FACT = ob.Button("ФАКТ", WIDTH // 2 - S(110), HEIGHT - S(130), S(220), S(70), FONT_BTN)

def skin_slots(page=0):
    per_row = 4
    slot_w = min(S(260), (WIDTH - S(40)) // per_row)
    start_x = WIDTH // 2 - slot_w * per_row // 2
    result = []
    for i in PAGES[page]:
        k = i - PAGES[page][0]
        row, col = divmod(k, per_row)
        y = S(140) if row == 0 else S(320)
        result.append((i, pygame.Rect(start_x + col * slot_w + (slot_w - S(95)) // 2,
                                      y, S(95), S(95))))
    return result

def draw_coin(surf, x, y, r):
    pygame.draw.circle(surf, COIN_COLOR, (x, y), r)
    pygame.draw.circle(surf, BLACK, (x, y), r, max(2, S(2)))

def main():
    global selected, coins, owned, best
    clock = pygame.time.Clock()
    pygame.display.set_caption("Динозаврик")
    build()

    state = "menu"
    skin_page = 0
    dino = ob.Dino(*skin_args())
    cacti = []
    puddles = []
    rain = ob.Rain()
    was_raining = False
    confirm_exit = False
    fact_lines = None
    score = 0
    speed = S(400)
    cactus_timer = 0.0
    puddle_timer = 0.0
    next_cactus = 1.0
    next_puddle = 1.0
    last_milestone = 0
    last_thousand = 0
    msg = ""
    msg_t = 0.0
    score_val = -1
    score_surf = None
    coin_val = -1
    coin_surf = None
    hint_surf = None

    def start_game():
        nonlocal dino, cacti, puddles, rain, score, speed, state
        nonlocal cactus_timer, puddle_timer, next_cactus, next_puddle, was_raining
        nonlocal last_milestone, last_thousand, confirm_exit
        dino = ob.Dino(*skin_args())
        cacti = []
        puddles = []
        rain = ob.Rain()
        was_raining = False
        confirm_exit = False
        if sounds:
            sounds.stop_rain()
        score = 0
        speed = S(400)
        cactus_timer = 0.0
        puddle_timer = 0.0
        next_cactus = 1.0
        next_puddle = 1.0
        last_milestone = 0
        last_thousand = 0
        state = "game"

    def new_fact():
        nonlocal fact_lines
        unseen = [i for i in range(len(FACTS)) if i not in facts_seen]
        pool = unseen if unseen else list(range(len(FACTS)))
        i = random.choice(pool)
        facts_seen.add(i)
        save_game()
        fact_lines = wrap(FACTS[i], WIDTH - S(160), FONT_TEXT)

    def draw_hud_coins():
        nonlocal coin_surf, coin_val
        if coins != coin_val:
            coin_val = coins
            coin_surf = FONT_TEXT.render(str(coins), True, BLACK)
        draw_coin(screen, WIDTH - S(120), S(37), S(16))
        screen.blit(coin_surf, (WIDTH - S(95), S(15)))

    while True:
        dt = clock.tick(FPS) / 1000
        if msg_t > 0:
            msg_t -= dt

        try:
            ws = pygame.display.get_window_size()
        except Exception:
            ws = (WIDTH, HEIGHT)
        if (ws[1] > ws[0]) != (HEIGHT > WIDTH):
            build()
            start_game()
            state = "menu"

        portrait = HEIGHT > WIDTH

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                if sounds:
                    sounds.stop_rain()
                pygame.quit()
                sys.exit()

            if portrait:
                continue

            tap = event.type == pygame.MOUSEBUTTONDOWN
            space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
            pos = event.pos if tap else None

            if tap or space:
                if state == "menu":
                    if space or BTN_PLAY.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        start_game()
                    elif BTN_SKINS.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        skin_page = 0
                        state = "skins"
                    elif BTN_CREDS.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        state = "credits"
                    elif BTN_FACTS.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        fact_lines = None
                        state = "facts"
                elif state == "facts":
                    if BTN_BACK_S.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        state = "menu"
                    elif space or BTN_FACT.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        new_fact()
                elif state == "skins":
                    if BTN_BACK_S.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        state = "menu"
                    elif tap and skin_page < MAX_PAGE and BTN_NEXT.clicked(pos):
                        skin_page += 1
                        if sounds:
                            sounds.play_click()
                    elif tap and skin_page > 0 and BTN_PREV.clicked(pos):
                        skin_page -= 1
                        if sounds:
                            sounds.play_click()
                    elif tap:
                        for i, r in skin_slots(skin_page):
                            if r.inflate(S(10), S(10)).collidepoint(pos):
                                name, color, price, outline, special = SKINS[i]
                                if i in owned:
                                    selected = i
                                    if sounds:
                                        sounds.play_skin()
                                    save_game()
                                elif coins >= price:
                                    coins -= price
                                    owned.add(i)
                                    selected = i
                                    msg = f"Куплен: {name}!"
                                    msg_t = 1.5
                                    if sounds:
                                        sounds.play_skin()
                                    save_game()
                                else:
                                    msg = f"Нужно {price} монет!"
                                    msg_t = 1.5
                elif state == "credits":
                    if space or BTN_BACK.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        state = "menu"
                elif state == "game":
                    if confirm_exit:
                        if tap and BTN_YES.clicked(pos):
                            confirm_exit = False
                            if sounds:
                                sounds.stop_rain()
                                sounds.play_click()
                            state = "menu"
                        elif tap and BTN_NO.clicked(pos):
                            confirm_exit = False
                            if sounds:
                                sounds.play_click()
                    elif tap and BTN_EXIT.clicked(pos):
                        confirm_exit = True
                        if sounds:
                            sounds.play_click()
                    elif dino.on_ground:
                        dino.jump()
                        if sounds:
                            sounds.play_jump()
                else:
                    if space or BTN_AGAIN.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        start_game()
                    elif BTN_MENU.clicked(pos):
                        if sounds:
                            sounds.play_click()
                        state = "menu"

        if portrait:
            screen.fill(WHITE)
            f = pygame.font.SysFont(None, max(24, WIDTH // 12), True)
            t = f.render("Поверни телефон", True, BLACK)
            screen.blit(t, ((WIDTH - t.get_width()) // 2, (HEIGHT - t.get_height()) // 2))
            pygame.display.flip()
            continue

        if state == "game" and not confirm_exit:
            score += dt * 10
            speed += S(6) * dt

            milestone = int(score // 200)
            if milestone > last_milestone:
                coins += milestone - last_milestone
                last_milestone = milestone
                msg = "+1 монета!"
                msg_t = 1.5
                if sounds:
                    sounds.play_coin()
            thousand = int(score // 1000)
            if thousand > last_thousand:
                coins += 5 * (thousand - last_thousand)
                last_thousand = thousand
                msg = "1000 метров! +5 монет!"
                msg_t = 2.0
                if sounds:
                    sounds.play_coin()

            rain.update(dt, score)
            if rain.raining() and not was_raining:
                if sounds:
                    sounds.start_rain()
            elif not rain.raining() and was_raining:
                if sounds:
                    sounds.stop_rain()
            was_raining = rain.raining()

            if rain.raining():
                puddle_timer += dt
                if puddle_timer >= next_puddle:
                    puddle_timer = 0.0
                    next_puddle = random.uniform(0.6, 1.3)
                    puddles.append(ob.Puddle(speed))
            else:
                cactus_timer += dt
                if cactus_timer >= next_cactus:
                    cactus_timer = 0.0
                    next_cactus = random.uniform(0.9, 1.8)
                    cacti.append(ob.Cactus(speed))

            dino.update(dt)
            for c in cacti[:]:
                c.update(dt)
                if c.x + c.w < -S(20):
                    cacti.remove(c)
                elif dino.hitbox().colliderect(c.hitbox()):
                    state = "over"
                    if int(score) > best:
                        best = int(score)
                    save_game()
            for p in puddles[:]:
                p.update(dt)
                if p.x + p.w < -S(20):
                    puddles.remove(p)
                elif dino.hitbox().colliderect(p.hitbox()):
                    state = "over"
                    if int(score) > best:
                        best = int(score)
                    save_game()
            if state == "over" and sounds:
                sounds.stop_rain()

        screen.fill(WHITE)

        if state == "menu":
            title = FONT_TITLE.render("ДИНОЗАВРИК", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, S(30)))
            rec = FONT_SMALL.render(f"Рекорд: {best}", True, (120, 120, 120))
            screen.blit(rec, (WIDTH // 2 - rec.get_width() // 2, S(128)))
            if HEIGHT >= S(450):
                prev = ob.dino_surface(SKINS[selected][1], max(2, S(110) // 24), 0,
                                       SKINS[selected][3], SKINS[selected][4],
                                       pygame.time.get_ticks() / 1000)
                screen.blit(prev, (WIDTH // 2 - prev.get_width() // 2, S(165)))
            BTN_PLAY.draw(screen)
            BTN_SKINS.draw(screen)
            BTN_CREDS.draw(screen)
            BTN_FACTS.draw(screen)
            draw_hud_coins()

        elif state == "facts":
            title = FONT_TITLE.render("ФАКТЫ", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, S(30)))
            idx = FONT_TEXT.render(f"Индекс: {len(facts_seen)}/{len(FACTS)}", True, (120, 120, 120))
            screen.blit(idx, (WIDTH - idx.get_width() - S(20), S(20)))
            if fact_lines is None:
                intro = wrap("Это факты! Нажми на кнопку ниже и ты узнаешь факт "
                             "об этой игре или из реального мира!", WIDTH - S(160), FONT_TEXT)
                y = int(HEIGHT * 0.35)
                for ln in intro:
                    t = FONT_TEXT.render(ln, True, BLACK)
                    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y))
                    y += S(55)
            else:
                y = int(HEIGHT * 0.35)
                for ln in fact_lines:
                    t = FONT_TEXT.render(ln, True, BLACK)
                    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y))
                    y += S(55)
            BTN_FACT.draw(screen)
            BTN_BACK_S.draw(screen)

        elif state == "skins":
            title = FONT_TITLE.render("СКИНЫ", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, S(30)))

            if skin_page == MAX_PAGE:
                sub = FONT_TEXT.render("Уникальные скины", True, (120, 120, 120))
                screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, S(120)))

            tt = pygame.time.get_ticks() / 1000
            for i, r in skin_slots(skin_page):
                name, color, price, outline, special = SKINS[i]
                is_owned = i in owned
                if skin_page == MAX_PAGE:
                    prev = ob.dino_surface(color, max(1, S(70) // 24), 0, outline, special, tt)
                else:
                    prev_color = color if is_owned else (160, 160, 160)
                    prev = ob.dino_surface(prev_color, max(1, S(70) // 24), 0,
                                           outline and is_owned, None, 0)
                screen.blit(prev, (r.centerx - prev.get_width() // 2,
                                   r.centery - prev.get_height() // 2))
                if not is_owned:
                    screen.blit(ob.lock_surf, (r.centerx - ob.lock_surf.get_width() // 2,
                                               r.centery - ob.lock_surf.get_height() // 2))
                if i == selected:
                    pygame.draw.rect(screen, BLACK, r.inflate(S(12), S(12)), max(2, S(3)))
                n = FONT_SMALL.render(name, True, BLACK)
                screen.blit(n, (r.centerx - n.get_width() // 2, r.bottom + S(10)))
                if not is_owned:
                    p = FONT_SMALL.render(str(price), True, BLACK)
                    draw_coin(screen, r.centerx - S(28), r.bottom + S(58), S(12))
                    screen.blit(p, (r.centerx - S(10), r.bottom + S(40)))

            if skin_page < MAX_PAGE:
                BTN_NEXT.draw(screen)
            if skin_page > 0:
                BTN_PREV.draw(screen)

            BTN_BACK_S.draw(screen)
            draw_hud_coins()

        elif state == "credits":
            title = FONT_TITLE.render("СОЗДАТЕЛИ", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, S(40)))
            lines = [
                "Эту игру создал",
                "11-летний разработчик",
                "вместе с ИИ Qwen",
                "",
                "Код: Python + pygame",
                "Дата: 6 августа 2026 года",
            ]
            y = int(HEIGHT * 0.28)
            for ln in lines:
                if ln:
                    t = FONT_TEXT.render(ln, True, BLACK)
                    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, y))
                y += S(40)
            BTN_BACK.draw(screen)
            draw_hud_coins()

        else:
            pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), max(2, S(3)))
            for p in puddles:
                p.draw(screen)
            for c in cacti:
                c.draw(screen)
            dino.draw(screen)
            rain.draw(screen)
            val = int(score)
            if val != score_val:
                score_val = val
                score_surf = FONT_TEXT.render(f"Счёт: {val}", True, BLACK)
            screen.blit(score_surf, (S(20), S(80)))
            if hint_surf is None:
                hint_surf = FONT_TEXT.render("Тап по экрану — прыжок", True, (150, 150, 150))
            screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - S(45)))
            draw_hud_coins()

            if state == "over":
                over = FONT_BTN.render("ИГРА ОКОНЧЕНА", True, BLACK)
                screen.blit(over, (WIDTH // 2 - over.get_width() // 2, int(HEIGHT * 0.22)))
                BTN_AGAIN.draw(screen)
                BTN_MENU.draw(screen)
            elif not confirm_exit:
                BTN_EXIT.draw(screen)

            if confirm_exit:
                dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dark.fill((255, 255, 255, 170))
                screen.blit(dark, (0, 0))
                q = FONT_BTN.render("Выйти из забега?", True, BLACK)
                screen.blit(q, (WIDTH // 2 - q.get_width() // 2, int(HEIGHT * 0.40)))
                BTN_NO.draw(screen)
                BTN_YES.draw(screen)

        if msg_t > 0 and msg:
            m = FONT_TEXT.render(msg, True, BLACK)
            screen.blit(m, (WIDTH // 2 - m.get_width() // 2, HEIGHT - S(60)))

        pygame.display.flip()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        err_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.txt")
        with open(err_path, "w") as f:
            traceback.print_exc(file=f)