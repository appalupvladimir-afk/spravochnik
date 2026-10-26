"""Общий движок для серий 2–8: озвучка (Piper), звуки, рисование сцен, рендер."""
import json, os, sys, subprocess, math, textwrap, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, '..', 'models')
SR = 44100
W, H, FPS, DUR = 720, 1280, 24, 60.0
PAD = 40
SW, SH = W + 2 * PAD, H + 2 * PAD
TITLE_T = 57.5

# ================= АУДИО =================
# голос: (модель, length_scale, сдвиг в полутонах)
VOICES = {
    'N': ('denis', 1.1, 0), 'HERO': ('denis', 1.0, 0), 'LENA': ('irina', 0.92, 1),
    'SEM': ('dmitri', 1.18, -3), 'MASHA': ('irina', 1.05, 5), 'GLEB': ('dmitri', 1.02, -1),
    'MIKH': ('denis', 1.05, -3), 'MOM': ('irina', 1.0, -2), 'DIKTOR': ('dmitri', 1.0, 0),
}
FX = {
    None: 'highpass=f=70,acompressor=threshold=-20dB:ratio=2.5,bass=g=2,aecho=0.8:0.6:20:0.06',
    'phone': 'highpass=f=350,lowpass=f=2800,volume=1.6',
    'radio': 'highpass=f=400,lowpass=f=3200,acrusher=bits=10:mix=0.3,volume=1.5',
    'mega': 'highpass=f=500,lowpass=f=3500,volume=3,alimiter=limit=0.6,aecho=0.8:0.7:180|360:0.35|0.2',
    'echo': 'highpass=f=80,aecho=0.8:0.75:120|260|400:0.4|0.28|0.15',
    'shout': 'highpass=f=90,volume=1.6,alimiter=limit=0.8,aecho=0.8:0.6:60:0.15',
}
_V = {}

def tts(key, text, fx, tag):
    from piper import PiperVoice
    from piper.config import SynthesisConfig
    model, ls, semi = VOICES[key]
    if model not in _V:
        _V[model] = PiperVoice.load(f'{MODELS}/vits-piper-ru_RU-{model}-medium/ru_RU-{model}-medium.onnx')
    v = _V[model]; sr = v.config.sample_rate
    cfg = SynthesisConfig(length_scale=ls, noise_scale=0.75, noise_w_scale=0.9)
    pause = 0.25 if fx in ('phone', 'shout') else 0.42
    parts = []
    for seg in text.split('|'):
        parts += [np.concatenate([c.audio_float_array for c in v.synthesize(seg, syn_config=cfg)]), np.zeros(int(sr * pause))]
    a = np.concatenate(parts[:-1])
    raw, out = f'/tmp/_{tag}_raw.wav', f'/tmp/_{tag}.wav'
    with wave.open(raw, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    f = 2 ** (semi / 12)
    af = (f'asetrate={int(sr * f)},aresample={sr},atempo={1 / f:.4f},' if semi else '') + FX[fx]
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', af, '-ar', str(SR), '-ac', '1', out], check=True)
    with wave.open(out) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x / (np.abs(x).max() + 1e-9) * 0.85

rng_a = np.random.default_rng(7)
def t2i(t): return int(t * SR)
def env(n, a=0.01, r=0.1):
    e = np.ones(n); ai, ri = min(n, int(a * SR)), min(n, int(r * SR))
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] = np.minimum(e[-ri:], np.linspace(1, 0, ri))
    return e
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
def noise(d): return rng_a.normal(0, 1, t2i(d))
def tt(d): return np.arange(t2i(d)) / SR
def norm(x): return x / (np.abs(x).max() + 1e-9)

# --- библиотека звуков (каждая функция возвращает массив) ---
def room(d): b = np.cumsum(noise(d)); b = b - lp(b, 20); return norm(b) * env(t2i(d), .5, .5)
def rumble(d): return norm(lp(noise(d), 70)) * np.exp(-tt(d) / (d / 2.5)) * env(t2i(d), .3, .3)
def wind(d): return norm(bp(noise(d), 200, 900)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * tt(d)) ** 2) * env(t2i(d), 1, 1)
def rain(d): return norm(hp(noise(d), 1500) * (1 + 0.3 * np.sin(tt(d) * 3))) * env(t2i(d), .8, .8)
def fire(d):
    x = norm(lp(noise(d), 600)) * 0.5
    for k in rng_a.uniform(0, d - .05, int(d * 14)):
        s = t2i(k); m = 300; x[s:s + m] += rng_a.normal(0, 1, m) * np.exp(-np.arange(m) / 40) * rng_a.uniform(.3, 1)
    return norm(x) * env(t2i(d), .3, .5)
def whoosh(d=1.2): return norm(bp(noise(d), 150, 3000)) * np.exp(-tt(d) / .35) * env(t2i(d), .03, .1)
def drip(): m = t2i(.25); return np.sin(2 * np.pi * (1800 - 3000 * tt(.25)) * tt(.25)) * np.exp(-tt(.25) / .03)
def step(): m = 1500; return bp(rng_a.normal(0, 1, m), 120, 1500) * np.exp(-np.arange(m) / 220)
def steps(d, rate=2.0, jit=0.05):
    x = np.zeros(t2i(d) + 2000); k = 0.0
    while k < d: s = t2i(k); x[s:s + 1500] += step() * rng_a.uniform(.6, 1); k += 1 / rate + rng_a.uniform(-jit, jit)
    return x
def crowd(d): return norm(bp(noise(d), 250, 1100)) * (0.6 + 0.4 * np.sin(2 * np.pi * .7 * tt(d)) ** 2) * env(t2i(d), .5, 1)
def siren(d):
    f = 550 + 300 * np.sin(2 * np.pi * tt(d) / 5 - np.pi / 2); p = np.cumsum(f) / SR
    return (np.sin(2 * np.pi * p) + .3 * np.sin(4 * np.pi * p)) * env(t2i(d), 2, 2)
def geiger(d, rate0, rate1):
    x = np.zeros(t2i(d) + 400); k = 0.0
    while k < d:
        r = rate0 + (rate1 - rate0) * (k / d); s = t2i(k)
        x[s:s + 300] += hp(rng_a.normal(0, 1, 300), 3000) * np.exp(-np.arange(300) / 25)
        k += rng_a.exponential(1 / r)
    return norm(x)
def knock(): return norm(lp(rng_a.normal(0, 1, 4000), 400) * np.exp(-np.arange(4000) / 500))
def clang(d=2.5):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / dd) for f, dd in [(180, .9), (431, .6), (797, .4), (1210, .25)])
    return norm(x + lp(noise(d), 800) * np.exp(-t / .05))
def creak(d=2.0):
    t = tt(d); f = 90 + 40 * np.sin(2 * np.pi * .7 * t); p = np.cumsum(f) / SR
    return norm(np.sign(np.sin(2 * np.pi * p)) * (0.5 + 0.5 * rng_a.random(len(t)))) * 0.6 * env(t2i(d), .2, .3)
def scrape(d): return norm(bp(noise(d), 1500, 5000) * (0.4 + 0.6 * (np.sin(2 * np.pi * 1.3 * tt(d)) > 0))) * env(t2i(d), .2, .2)
def gunshot(): d = 1.6; t = tt(d); return norm(lp(noise(d), 3000) * np.exp(-t / .06) + np.sin(2 * np.pi * 60 * t) * np.exp(-t / .25) + lp(noise(d), 500) * np.exp(-t / .6) * .4)
def thump(): d = .6; t = tt(d); return norm(np.sin(2 * np.pi * 70 * t) * np.exp(-t / .12) + lp(noise(d), 600) * np.exp(-t / .05))
def crickets(d):
    t = tt(d); g = (np.sin(2 * np.pi * 18 * t) > .3) * (np.sin(2 * np.pi * .6 * t) > -.2)
    return norm(np.sin(2 * np.pi * 4300 * t) * g + np.sin(2 * np.pi * 3900 * t) * np.roll(g, 9000) * .6) * env(t2i(d), 1, 1)
def birds(d):
    x = np.zeros(t2i(d) + t2i(.4))
    for k in rng_a.uniform(0, d, int(d * 1.2)):
        m = t2i(rng_a.uniform(.08, .25)); t = np.arange(m) / SR; f0 = rng_a.uniform(2500, 4500)
        x[t2i(k):t2i(k) + m] += np.sin(2 * np.pi * (f0 + 1500 * np.sin(2 * np.pi * 25 * t)) * t) * np.sin(np.pi * t / t[-1])
    return norm(x)
def engine(d): t = tt(d); return norm(lp(np.sign(np.sin(2 * np.pi * 38 * t)) + noise(d) * .3, 300)) * env(t2i(d), 1.5, 2)
def dogs(n=4):
    x = np.zeros(t2i(4))
    for k in range(n):
        m = t2i(.18); t = np.arange(m) / SR; s = t2i(.2 + k * .7 + rng_a.uniform(0, .2))
        x[s:s + m] += bp(np.sign(np.sin(2 * np.pi * 420 * t)) + rng_a.normal(0, .5, m), 300, 2500) * np.sin(np.pi * t / t[-1])
    return norm(x)
def static(d): return norm(bp(noise(d), 800, 6000) * (0.7 + 0.3 * rng_a.random(t2i(d)))) * env(t2i(d), .05, .05)
def drone(d, f0=45, f1=55): t = tt(d); return np.sin(2 * np.pi * (f0 + (f1 - f0) * t / d / 2) * t) * env(t2i(d), d * .4, .5)
def bass_hit(): d = 2.4; t = tt(d); return np.sin(2 * np.pi * 42 * t) * np.exp(-t / .7) + lp(noise(d), 200) * np.exp(-t / .15) * .5
def heartbeat(d, bpm=70):
    x = np.zeros(t2i(d) + t2i(.5)); k = 0.0
    while k < d:
        for o in (0, .22): s = t2i(k + o); x[s:s + t2i(.2)] += np.sin(2 * np.pi * 50 * tt(.2)) * np.exp(-tt(.2) / .05)
        k += 60 / bpm
    return norm(x)
def child_cry(d):
    t = tt(d); f = 420 + 60 * np.sin(2 * np.pi * 5 * t); p = np.cumsum(f) / SR
    g = (np.sin(2 * np.pi * .45 * t) > -.1).astype(float)
    return norm(bp(np.sin(2 * np.pi * p) + .4 * np.sin(4 * np.pi * p) + rng_a.normal(0, .2, len(t)), 300, 2500) * lp(g, 8))
def boards(): return norm(np.concatenate([creak(.5) * .5, lp(noise(.3), 1500) * np.exp(-tt(.3) / .05)]))
def hug_music(d):
    t = tt(d); x = np.zeros_like(t)
    for f in (220, 277.2, 329.6, 440): x += np.sin(2 * np.pi * f * t) * (0.6 + 0.4 * np.sin(2 * np.pi * .2 * t))
    return norm(lp(x, 1500)) * env(t2i(d), 1.5, 1.5)

def build_audio(lines, sfx_events, out_wav, subs_json, tag):
    N = t2i(DUR); vo = np.zeros(N); sfx = np.zeros(N); subs = []
    def add(buf, x, t, g):
        s = t2i(t); e = min(N, s + len(x))
        if e > s: buf[s:e] += x[:e - s] * g
    for k, (t0, who, text, sub, fx) in enumerate(lines):
        a = tts(who, text, fx, f'{tag}_{k}')
        if fx == 'phone' or fx == 'radio': a = a + norm(bp(rng_a.normal(0, 1, len(a)), 1000, 4000)) * .05
        add(vo, a, t0, 1.0)
        subs.append({'t0': t0, 't1': t0 + len(a) / SR, 'text': sub, 'who': who})
        print(f'  {who:6} {t0:5.1f}-{t0 + len(a) / SR:5.1f}  {text[:50]}')
    for t0, x, g in sfx_events: add(sfx, x, t0, g)
    duck = 1 - 0.5 * np.clip(lp(np.abs(vo), 5) / 0.05, 0, 1)
    mix = np.tanh((vo + sfx * duck) * 1.1) * 0.95
    mix[-t2i(.05):] *= np.linspace(1, 0, t2i(.05))
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    json.dump(subs, open(subs_json, 'w'), ensure_ascii=False, indent=1)
    return subs

# ================= ВИДЕО =================
FD = '/usr/share/fonts/truetype/dejavu/'
_fc = {}
def font(s, b=True):
    k = (s, b)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
    return _fc[k]
rng = np.random.default_rng(3)
def lerp(a, b, x): return a + (b - a) * max(0, min(1, x))
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def grad(w, h, top, bot):
    a = np.linspace(0, 1, h)[:, None, None]
    g = np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a
    return Image.fromarray(np.repeat(g, w, 1).astype(np.uint8))
def canvas(top=(30, 32, 34), bot=(20, 21, 22)): return grad(SW, SH, top, bot)
def city(d, w, base, rs, col=(14, 17, 20), lit=0.15, scale=1.0):
    x = -20
    while x < w:
        bw = int(rs.integers(90, 170) * scale); bh = int(rs.integers(160, 420) * scale)
        d.rectangle([x, base - bh, x + bw, base], fill=col)
        for wy in range(base - bh + 14, base - 10, max(4, int(22 * scale))):
            for wx in range(x + 8, x + bw - 10, max(4, int(18 * scale))):
                if rs.random() < lit:
                    d.rectangle([wx, wy, wx + int(7 * scale), wy + int(9 * scale)], fill=(int(rs.integers(90, 140)), int(rs.integers(80, 110)), 50))
        x += bw + int(rs.integers(6, 40))
def car(d, x, y, c=(12, 13, 14), s=1.0, tail=False):
    d.rounded_rectangle([x, y, x + 200 * s, y + 70 * s], int(18 * s), fill=c); d.rounded_rectangle([x + 35 * s, y - 45 * s, x + 160 * s, y + 10 * s], int(22 * s), fill=c)
    d.ellipse([x + 25 * s, y + 50 * s, x + 65 * s, y + 90 * s], fill=(5, 5, 5)); d.ellipse([x + 135 * s, y + 50 * s, x + 175 * s, y + 90 * s], fill=(5, 5, 5))
    if tail:
        for lx in (x + 6 * s, x + 170 * s): d.rectangle([lx, y + 12 * s, lx + 24 * s, y + 28 * s], fill=(200, 30, 25))

# цвета персонажей (силуэты с оттенком одежды)
HERO_C, LENA_C, SEM_C, MASHA_C = (30, 36, 22), (70, 18, 16), (22, 26, 36), (120, 100, 20)
GLEB_C, MIKH_C, MOM_C, SOLD_C = (28, 32, 22), (48, 34, 24), (40, 30, 34), (24, 28, 22)
def person(d, cx, base, s, col, cap=False, pony=False, braids=False, bun=False, arms_up=False, bulky=False, gun=False, light=None):
    hr = 34 * s; hy = base - 330 * s; bw = 85 if bulky else 70
    d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=col)
    if pony: d.ellipse([cx + hr * .7, hy - hr * .1, cx + hr * 1.15, hy + hr * 1.2], fill=col)
    if braids:
        for sx in (-1, 1): d.rectangle([cx + sx * hr * .9 - 6 * s, hy, cx + sx * hr * .9 + 6 * s, hy + hr * 1.6], fill=col)
    if bun: d.ellipse([cx - hr * .5, hy - hr * 1.5, cx + hr * .5, hy - hr * .6], fill=col)
    if cap: d.rectangle([cx - hr * 1.15, hy - hr, cx + hr * 1.3, hy - hr * .45], fill=col)
    d.polygon([(cx - bw * s, base - 280 * s), (cx + bw * s, base - 280 * s), (cx + (bw + 15) * s, base - 80 * s), (cx - (bw + 15) * s, base - 80 * s)], fill=col)
    d.rectangle([cx - 60 * s, base - 85 * s, cx - 15 * s, base], fill=col); d.rectangle([cx + 15 * s, base - 85 * s, cx + 60 * s, base], fill=col)
    if arms_up:
        for sx in (-1, 1): d.polygon([(cx + sx * 55 * s, base - 270 * s), (cx + sx * 80 * s, base - 270 * s), (cx + sx * 110 * s, base - 470 * s), (cx + sx * 85 * s, base - 470 * s)], fill=col)
    if gun: d.line([cx + 40 * s, base - 200 * s, cx + 160 * s, base - 240 * s], fill=col, width=int(12 * s))
    if light: d.ellipse([cx + 50 * s, base - 215 * s, cx + 72 * s, base - 193 * s], fill=light)
def cone(im, x, y, ang, spread, length, alpha=110, col=(230, 225, 190)):
    """Луч фонаря/прожектора."""
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a1, a2 = math.radians(ang - spread), math.radians(ang + spread)
    d.polygon([(x, y), (x + math.cos(a1) * length, y + math.sin(a1) * length), (x + math.cos(a2) * length, y + math.sin(a2) * length)], fill=col + (alpha,))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(25)))
def glow(im, x, y, r, col, a=160):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(r * .6)))
def trees(d, rs, base, n, hmin, hmax, col, w=SW):
    for _ in range(n):
        x = rs.uniform(-40, w + 40); h = rs.uniform(hmin, hmax); bw = h * .18
        d.rectangle([x - bw * .08, base - h * .2, x + bw * .08, base], fill=col)
        for k in range(5):
            y0 = base - h * .2 - k * h * .17; ww = bw * (1 - k * .17)
            d.polygon([(x - ww, y0), (x + ww, y0), (x, y0 - h * .3)], fill=col)
def zoom(im, z, cx=.5, cy=.5):
    if z == 1: return im
    w, h = im.size; nw, nh = int(w * z), int(h * z); im = im.resize((nw, nh))
    x = int((nw - w) * cx); y = int((nh - h) * cy); return im.crop((x, y, x + w, y + h))
def particles(im, t, n, col, speed, size, seed, drift=0.0, streak=0):
    d = ImageDraw.Draw(im); rs = np.random.default_rng(seed)
    xs = rs.uniform(0, SW, n); ys = rs.uniform(0, SH, n); sp = rs.uniform(.6, 1.4, n)
    for x, y, s in zip(xs, ys, sp):
        yy = (y + t * speed * s) % SH; xx = (x + t * drift * s + math.sin(t + y) * 10) % SW
        if streak: d.line([xx, yy, xx - 4, yy - streak], fill=col, width=1)
        else: d.ellipse([xx - size, yy - size, xx + size, yy + size], fill=col)

VIG = None
def finish(im, t, subs, shake=0.0, white=0.0, dark=0.0, warm=False):
    global VIG
    ox = int(PAD + rng.normal(0, shake)); oy = int(PAD + rng.normal(0, shake))
    im = im.convert('RGB').crop((ox, oy, ox + W, oy + H))
    a = np.asarray(im, np.float32)
    lum = a.mean(2, keepdims=True); a = lum + (a - lum) * (0.85 if warm else 0.62)
    a = a * (np.array([1.08, 0.98, 0.82]) if warm else np.array([0.92, 1.0, 1.0])) + (np.array([6, 2, 0]) if warm else np.array([0, 4, 6]))
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2)
        VIG = np.clip(1.15 - r * 0.75, 0.25, 1)[..., None]
    a = a * VIG * (1 - dark)
    a = a * (1 - white) + 255 * white
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for s in subs:
        if s['t0'] - 0.05 <= t <= s['t1'] + 0.35:
            lines = textwrap.wrap(s['text'], 26); y = H - 150 - 50 * (len(lines) - 1)
            for ln in lines:
                d.text((W / 2, y), ln, font=font(38), fill=(255, 255, 255), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0)); y += 50
    return im

def title(t, n, extra='Продолжение следует…', name='ГОРОД Z', sub=None):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    if t > TITLE_T + .5:
        a = int(255 * ease((t - TITLE_T - .5) / .5))
        d.text((W / 2, H / 2 - 60), name, font=font(84), fill=(a, int(a * .25), int(a * .2)), anchor='mm')
        d.text((W / 2, H / 2 + 30), '140 КИЛОМЕТРОВ', font=font(34), fill=(a, a, a), anchor='mm')
        d.text((W / 2, H / 2 + 120), sub or f'Серия {n} из 8 · {extra}', font=font(26, False), fill=(int(a * .7),) * 3, anchor='mm')
    return im

def render(frame_fn, wav, out, previews=None):
    if previews:
        ims = [frame_fn(t).resize((240, 427)) for t in previews]
        sheet = Image.new('RGB', (240 * 6, 427 * math.ceil(len(ims) / 6)))
        for i, im in enumerate(ims): sheet.paste(im, ((i % 6) * 240, (i // 6) * 427))
        sheet.save(out.replace('.mp4', '_sheet.jpg')); return
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                           '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(frame_fn(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()

def run(n, lines, sfx_fn, frame_factory):
    """sfx_fn() -> список (t, массив, громкость); frame_factory(subs) -> frame(t)."""
    tag = f'ep{n}'; wav = os.path.join(HERE, f'{tag}.wav'); sj = os.path.join(HERE, f'{tag}_subs.json')
    out = os.path.join(HERE, f'Gorod_Z_seriya_{n}.mp4')
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('audio', 'all'):
        print(f'== серия {n}: озвучка'); build_audio(lines, sfx_fn(), wav, sj, tag)
    subs = json.load(open(sj))
    frame = frame_factory(subs)
    if mode == 'preview':
        render(frame, wav, out, previews=[float(x) for x in sys.argv[2].split(',')])
    elif mode in ('video', 'all'):
        render(frame, wav, out); print('готово:', out)
