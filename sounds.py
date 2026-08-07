# sounds.py — все звуки игры, генерируются кодом, файлы не нужны
import pygame
import struct
import random

RATE = 22050
_ok = False

S_JUMP = S_CLICK = S_SKIN = S_COIN = S_RAIN = None

def _pack(v):
    return struct.pack("<h", int(max(-1, min(1, v)) * 32767))

def _env(i, n):
    # сглаживает края ноты, чтобы не щёлкало
    fade = int(RATE * 0.005)
    if i < fade:
        return i / fade
    if i > n - fade:
        return (n - i) / fade
    return 1.0

def _tone(freq, dur, vol=0.2):
    n = int(RATE * dur)
    buf = bytearray()
    for i in range(n):
        t = i / RATE
        v = vol if (t * freq) % 1.0 < 0.5 else -vol
        buf += _pack(v * _env(i, n))
    return pygame.mixer.Sound(buffer=bytes(buf))

def _sweep(f0, f1, dur, vol=0.25):
    n = int(RATE * dur)
    buf = bytearray()
    phase = 0.0
    for i in range(n):
        phase += (f0 + (f1 - f0) * i / n) / RATE
        v = vol if phase % 1.0 < 0.5 else -vol
        buf += _pack(v * _env(i, n))
    return pygame.mixer.Sound(buffer=bytes(buf))

def _join(sounds, gap=0.03):
    raw = b""
    g = bytes(int(RATE * gap) * 2)
    for s in sounds:
        raw += s.get_raw() + g
    return pygame.mixer.Sound(buffer=raw)

def _noise(dur, vol):
    """Сглаженный белый шум — звучит как дождь."""
    n = int(RATE * dur)
    buf = bytearray()
    prev = 0.0
    for i in range(n):
        v = (random.random() * 2 - 1) * 0.6 + prev * 0.4
        prev = v
        buf += _pack(v * vol)
    return pygame.mixer.Sound(buffer=bytes(buf))

def init():
    global S_JUMP, S_CLICK, S_SKIN, S_COIN, S_RAIN, _ok
    try:
        pygame.mixer.init(RATE, -16, 1, 512)
    except Exception:
        try:
            pygame.mixer.init()
        except Exception:
            return
    _ok = True
    S_JUMP = _sweep(250, 700, 0.15)                                  # прыжок
    S_CLICK = _tone(700, 0.06, 0.18)                                # щелчок кнопки
    S_SKIN = _join([_tone(500, 0.08), _tone(800, 0.1)])             # смена скина
    S_COIN = _join([_tone(900, 0.07), _tone(1400, 0.12)], gap=0.02) # монетка
    S_RAIN = _noise(2.0, 0.12)                                      # шум дождя

def play_jump():
    if _ok and S_JUMP:
        S_JUMP.play()

def play_click():
    if _ok and S_CLICK:
        S_CLICK.play()

def play_skin():
    if _ok and S_SKIN:
        S_SKIN.play()

def play_coin():
    if _ok and S_COIN:
        S_COIN.play()

def start_rain():
    if _ok and S_RAIN:
        S_RAIN.play(loops=-1)   # крутится, пока не остановим

def stop_rain():
    if _ok and S_RAIN:
        S_RAIN.stop()

# Песня убрана по желанию Матвея — функции-заглушки
def start_music():
    pass

def stop_music():
    pass