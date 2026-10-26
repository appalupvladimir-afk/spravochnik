import json, os, sys, subprocess, math, textwrap, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS, DUR = 720, 1280, 24, 60.0
PAD = 40  # extra margin for camera shake
F = '/usr/share/fonts/truetype/dejavu/'
font = lambda s, b=True: ImageFont.truetype(F + ('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf'), s)
rng = np.random.default_rng(3)
subs = json.load(open('subs.json'))
ONLY = float(sys.argv[1]) if len(sys.argv) > 1 else None

def lerp(a, b, x): return a + (b - a) * max(0, min(1, x))
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def grad(w, h, top, bot):
    a = np.linspace(0, 1, h)[:, None, None]
    g = np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a
    return Image.fromarray(np.repeat(g, w, 1).astype(np.uint8))

def city(d, w, base, rs, col=(14, 17, 20), lit=0.15, scale=1.0):
    """Ряд советских панелек: силуэты с окнами."""
    x = -20
    while x < w:
        bw = int(rs.integers(90, 170) * scale); bh = int(rs.integers(160, 420) * scale)
        d.rectangle([x, base - bh, x + bw, base], fill=col)
        for wy in range(base - bh + 14, base - 10, int(22 * scale)):
            for wx in range(x + 8, x + bw - 10, int(18 * scale)):
                if rs.random() < lit:
                    c = (int(rs.integers(90, 140)), int(rs.integers(80, 110)), 50)
                    d.rectangle([wx, wy, wx + int(7 * scale), wy + int(9 * scale)], fill=c)
        x += bw + int(rs.integers(6, 40))

# ---------- статичные фоны ----------
SW, SH = W + 2 * PAD, H + 2 * PAD
def bg_window():
    im = Image.new('RGB', (SW, SH), (10, 12, 15)); d = ImageDraw.Draw(im)
    sky = grad(470, 560, (70, 82, 88), (120, 125, 118)); im.paste(sky, (165, 220))
    win = Image.new('RGB', (470, 560)); win.paste(sky); wd = ImageDraw.Draw(win)
    city(wd, 470, 560, np.random.default_rng(1), (30, 34, 38), 0.05, 0.6)
    city(wd, 470, 560, np.random.default_rng(2), (18, 21, 24), 0.1, 0.9)
    im.paste(win, (165, 220))
    for r in [[155, 210, 645, 230], [155, 770, 645, 790], [155, 210, 175, 790], [625, 210, 645, 790], [392, 210, 412, 790], [155, 480, 645, 496]]:
        d.rectangle(r, fill=(38, 40, 42))
    d.rectangle([100, 790, 700, 830], fill=(32, 33, 34))  # подоконник
    d.rectangle([520, 740, 560, 790], fill=(70, 60, 50)); d.ellipse([520, 732, 560, 748], fill=(80, 70, 58))  # кружка
    return im
def bg_yard():
    im = grad(SW, SH, (95, 70, 55), (60, 64, 66)); d = ImageDraw.Draw(im)
    city(d, SW, 900, np.random.default_rng(5), (40, 40, 42), 0.04, 0.9)
    city(d, SW, 980, np.random.default_rng(6), (22, 24, 26), 0.08, 1.4)
    d.rectangle([0, 980, SW, SH], fill=(28, 30, 31))
    return im
CARS = [(30, 1060), (250, 1080), (470, 1060), (120, 1180), (400, 1200), (640, 1170)]
def car(d, x, y, c=(12, 13, 14)):
    d.rounded_rectangle([x, y, x + 200, y + 70], 18, fill=c); d.rounded_rectangle([x + 35, y - 45, x + 160, y + 10], 22, fill=c)
    d.ellipse([x + 25, y + 50, x + 65, y + 90], fill=(5, 5, 5)); d.ellipse([x + 135, y + 50, x + 175, y + 90], fill=(5, 5, 5))
def bg_hall():
    im = Image.new('RGB', (SW, SH), (14, 15, 16)); d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (260, 300), (260, 1100), (0, SH)], fill=(24, 26, 26))
    d.polygon([(SW, 0), (540, 300), (540, 1100), (SW, SH)], fill=(20, 22, 22))
    d.polygon([(0, SH), (260, 1100), (540, 1100), (SW, SH)], fill=(30, 28, 25))
    d.rectangle([300, 420, 500, 1100], fill=(150, 145, 130))  # дверной проём со светом
    return im.filter(ImageFilter.GaussianBlur(2))
def bg_table():
    im = grad(SW, SH, (52, 38, 28), (34, 25, 18)); d = ImageDraw.Draw(im)
    rs = np.random.default_rng(9)
    for y in range(0, SH, 7):
        d.line([0, y + rs.integers(-2, 3), SW, y + rs.integers(-2, 3)], fill=(60 + rs.integers(-8, 8), 44, 31), width=1)
    return im.filter(ImageFilter.GaussianBlur(1.2))
def bg_stairs():
    im = grad(SW, SH, (52, 60, 56), (34, 38, 36)); d = ImageDraw.Draw(im)
    d.rectangle([0, 820, SW, SH], fill=(46, 46, 44))
    for i in range(14):  # ступени вниз-вправо
        x = min(420 + i * 30, SW - 1); y = 820 + i * 34
        d.rectangle([x, y, SW, y + 34], fill=(56 - i, 56 - i, 54 - i)); d.line([x, y, SW, y], fill=(70, 70, 66), width=2)
    for i in range(10):  # перила
        d.line([440 + i * 30, 700 + i * 34, 440 + i * 30, 820 + i * 34], fill=(25, 25, 25), width=4)
    d.line([430, 690, 800, 1110], fill=(60, 30, 25), width=10)
    d.rectangle([90, 380, 330, 830], fill=(70, 52, 38)); d.rectangle([100, 390, 320, 820], outline=(50, 38, 28), width=4)
    d.ellipse([280, 600, 300, 620], fill=(150, 140, 100))
    d.text((180, 300), '47', font=font(40), fill=(140, 150, 140))
    d.rectangle([0, 0, SW, 120], fill=(40, 46, 44)); d.ellipse([340, 90, 420, 130], fill=(200, 190, 140))  # лампа
    return im
def bg_nuke():
    im = grad(SW, SH, (40, 38, 40), (150, 95, 55)); return im
BG = {'window': bg_window(), 'yard': bg_yard(), 'hall': bg_hall(), 'table': bg_table(), 'stairs': bg_stairs(), 'nuke': bg_nuke()}
YARD_BLUR = BG['yard'].filter(ImageFilter.GaussianBlur(18))
NUKE_CITY = Image.new('RGBA', (SW, SH), (0, 0, 0, 0)); city(ImageDraw.Draw(NUKE_CITY), SW, 1150, np.random.default_rng(11), (15, 15, 17, 255), 0.0, 1.0)

def person(d, cx, base, s, col, cap=False, pony=False):
    hr = 34 * s
    d.ellipse([cx - hr, base - 330 * s - hr, cx + hr, base - 330 * s + hr], fill=col)
    if pony: d.ellipse([cx + hr * .7, base - 330 * s - hr * .1, cx + hr * 1.15, base - 330 * s + hr * 1.2], fill=col)
    if cap: d.rectangle([cx - hr * 1.15, base - 330 * s - hr * 1.0, cx + hr * 1.3, base - 330 * s - hr * .45], fill=col)
    d.polygon([(cx - 70 * s, base - 280 * s), (cx + 70 * s, base - 280 * s), (cx + 85 * s, base - 80 * s), (cx - 85 * s, base - 80 * s)], fill=col)
    d.rectangle([cx - 60 * s, base - 85 * s, cx - 15 * s, base], fill=col); d.rectangle([cx + 15 * s, base - 85 * s, cx + 60 * s, base], fill=col)

def phone_screen(t, mode):
    im = Image.new('RGBA', (440, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 439, 899], 54, fill=(12, 12, 14))
    sc = grad(400, 860, (40, 52, 60), (18, 22, 26)).convert('RGBA'); m = Image.new('L', (400, 860), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 399, 859], 42, fill=255); im.paste(sc, (20, 20), m)
    d.text((50, 40), '7:47', font=font(24), fill=(230, 230, 230))
    if mode == 'nosig':
        d.text((260, 40), 'Нет сети', font=font(22, False), fill=(230, 120, 110))
    else:
        for i in range(4): d.rectangle([370 + i * 9, 62 - i * 6, 376 + i * 9, 66], fill=(230, 230, 230) if i < 2 else (90, 90, 90))
    if mode in ('ring', 'call'):
        d.ellipse([140, 150, 300, 310], fill=(150, 120, 110)); d.text((193, 190), 'М', font=font(70), fill=(255, 255, 255))
        d.text((220, 360), 'Мама', font=font(52), fill=(255, 255, 255), anchor='mm')
        if mode == 'ring':
            d.text((220, 420), 'мобильный', font=font(24, False), fill=(190, 190, 190), anchor='mm')
            p = 1 + 0.08 * math.sin(t * 8)
            for x, c in [(110, (220, 60, 50)), (330, (60, 190, 90))]:
                r = 48 * (p if c[1] > 100 else 1); d.ellipse([x - r, 760 - r, x + r, 760 + r], fill=c)
        else:
            sec = int(max(0, t - 39.4)); d.text((220, 420), f'00:0{sec}', font=font(26, False), fill=(200, 200, 200), anchor='mm')
            for i in range(24):
                hgt = 6 + abs(math.sin(t * 13 + i * 1.7)) * 70 * (rng.random() * .6 + .4)
                d.rectangle([70 + i * 13, 560 - hgt / 2, 78 + i * 13, 560 + hgt / 2], fill=(110, 200, 140))
            d.ellipse([172, 712, 268, 808], fill=(220, 60, 50))
    else:
        d.text((220, 330), 'Вызов', font=font(46), fill=(230, 230, 230), anchor='mm')
        d.text((220, 390), 'завершён', font=font(46), fill=(230, 230, 230), anchor='mm')
        d.text((220, 470), 'Мама · 00:03', font=font(24, False), fill=(170, 170, 170), anchor='mm')
        if t > 47.5:
            a = int(255 * ease((t - 47.5) / .6)); ov = Image.new('RGBA', (440, 900), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([50, 560, 390, 660], 20, fill=(60, 20, 20, a)); od.text((220, 610), '⚠ Нет сети', font=font(32), fill=(255, 140, 130, a), anchor='mm')
            im = Image.alpha_composite(im, ov)
    return im

def news_phone():
    im = Image.new('RGBA', (300, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 299, 559], 36, fill=(10, 10, 12)); d.rounded_rectangle([12, 12, 287, 547], 28, fill=(225, 228, 230))
    d.text((30, 30), 'Новости', font=font(26), fill=(30, 30, 30))
    for i in range(6):
        y = 90 + i * 74; d.rectangle([30, y, 100, y + 56], fill=(150, 160, 170))
        d.rectangle([112, y + 4, 268, y + 14], fill=(110, 110, 110)); d.rectangle([112, y + 24, 240, y + 32], fill=(170, 170, 170))
    return im.rotate(-8, expand=True, resample=Image.BICUBIC)
NEWS = news_phone()

ITEMS = [('ВОДА', 16.0), ('ПАСПОРТА', 17.4), ('АПТЕЧКА', 18.8), ('ФОНАРИК', 20.2), ('РАДИО', 21.6)]
def draw_item(d, name, cx, cy):
    if name == 'ВОДА':
        d.rounded_rectangle([cx - 30, cy - 90, cx + 30, cy + 90], 14, fill=(120, 160, 190)); d.rectangle([cx - 14, cy - 110, cx + 14, cy - 88], fill=(40, 90, 160))
    elif name == 'ПАСПОРТА':
        for k in range(2): d.rectangle([cx - 60 + k * 18, cy - 80 + k * 14, cx + 40 + k * 18, cy + 60 + k * 14], fill=(120, 30, 30), outline=(80, 20, 20), width=3)
        d.text((cx - 22, cy - 30), '★', font=font(40), fill=(200, 170, 80))
    elif name == 'АПТЕЧКА':
        d.rounded_rectangle([cx - 80, cy - 60, cx + 80, cy + 60], 12, fill=(225, 225, 220)); d.rectangle([cx - 12, cy - 40, cx + 12, cy + 40], fill=(200, 40, 40)); d.rectangle([cx - 40, cy - 12, cx + 40, cy + 12], fill=(200, 40, 40))
    elif name == 'ФОНАРИК':
        d.rounded_rectangle([cx - 90, cy - 18, cx + 50, cy + 18], 8, fill=(40, 40, 44)); d.polygon([(cx + 50, cy - 18), (cx + 90, cy - 34), (cx + 90, cy + 34), (cx + 50, cy + 18)], fill=(60, 60, 64))
    else:
        d.rounded_rectangle([cx - 90, cy - 55, cx + 90, cy + 55], 10, fill=(70, 75, 70)); d.ellipse([cx - 75, cy - 40, cx - 5, cy + 30], fill=(40, 40, 40)); d.line([cx + 60, cy - 55, cx + 110, cy - 130], fill=(150, 150, 150), width=4)
SLOTS = [(200, 330), (500, 360), (220, 660), (500, 700), (360, 980)]

VIG = None
def finish(im, t, shake=0.0, white=0.0, dark=0.0):
    global VIG
    ox = int(PAD + rng.normal(0, shake)); oy = int(PAD + rng.normal(0, shake))
    im = im.crop((ox, oy, ox + W, oy + H))
    a = np.asarray(im.convert('RGB'), np.float32)
    lum = a.mean(2, keepdims=True); a = lum + (a - lum) * 0.62  # десатурация
    a = a * np.array([0.92, 1.0, 1.0]) + np.array([0, 4, 6])  # холодный грейд
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2)
        VIG = np.clip(1.15 - r * 0.75, 0.25, 1)[..., None]
    a = a * VIG * (1 - dark)
    a += rng.normal(0, 7, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    a = a * (1 - white) + 255 * white
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return subtitle(im, t)

def subtitle(im, t):
    for s in subs:
        if s['t0'] - 0.05 <= t <= s['t1'] + 0.35:
            d = ImageDraw.Draw(im); f = font(38); lines = textwrap.wrap(s['text'], 26)
            y = H - 150 - 50 * (len(lines) - 1)
            for ln in lines:
                d.text((W / 2, y), ln, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0)); y += 50
    return im

def frame(t):
    if t < 5:  # окно, вспышка
        im = BG['window'].copy().convert('RGBA'); z = 1 + t * 0.012
        ph = NEWS; im.alpha_composite(ph, (int(260 + PAD - t * 3), int(840 + PAD)))
        im = im.convert('RGB').resize((int(SW * z), int(SH * z))); dx = (im.width - SW) // 2; im = im.crop((dx, dx, dx + SW, dx + SH))
        if t > 4.3:
            fl = ease((t - 4.3) / 0.45); win = Image.new('RGB', im.size, (255, 255, 250))
            m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rectangle([165 + PAD // 2, 220, 635, 780], fill=255)
            im = Image.composite(win, im, m.filter(ImageFilter.GaussianBlur(30)))
            return finish(im, t, white=fl * 0.95)
        return finish(im, t)
    if t < 10:  # двор: дрожь, сигнализации
        im = BG['yard'].copy(); d = ImageDraw.Draw(im)
        for i, (x, y) in enumerate(CARS):
            car(d, x, y)
            if (t * 2.5 + i * .5) % 1 < .5 and t > 6:
                for lx in (x + 8, x + 180): d.ellipse([lx - 10, y + 15, lx + 18, y + 40], fill=(255, 170, 40))
        glow = Image.new('RGB', im.size, (255, 140, 60)); m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).ellipse([-200, 500, SW + 200, 1100], fill=int(90 * max(0, 1 - (t - 5) / 6)))
        im = Image.composite(glow, im, m.filter(ImageFilter.GaussianBlur(80)))
        return finish(im, t, shake=max(0, 14 * (1 - (t - 5) / 3.5)), white=max(0, 0.9 - (t - 5) * 1.3))
    if t < 15:  # коридор, Лена
        im = BG['hall'].copy(); d = ImageDraw.Draw(im); p = ease((t - 10) / 4.5)
        s = lerp(0.9, 2.6, p); person(d, 400 + math.sin(t * 9) * 6 * (1 - p), int(lerp(1100, 1500, p)), s, (60, 18, 16), pony=True)
        return finish(im.filter(ImageFilter.GaussianBlur(1 + 2 * p)), t, shake=3)
    if t < 25:  # сборы, свет гаснет
        im = BG['table'].copy(); d = ImageDraw.Draw(im)
        for (name, t0), (cx, cy) in zip(ITEMS, SLOTS):
            if t >= t0:
                p = ease((t - t0) / 0.3); draw_item(d, name, cx + PAD, int(cy + PAD - (1 - p) * 120))
                d.text((cx + PAD, cy + PAD + 130), name, font=font(26), fill=(230, 220, 200), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0))
        dark = 0.0
        if 22.6 <= t < 23.6: dark = 0.8 if (t * 13) % 1 < 0.45 else 0.1
        elif t >= 23.6: dark = 0.72
        return finish(im, t, shake=1.5, dark=dark)
    if t < 35:  # подъезд, Семёныч
        im = BG['stairs'].copy().convert('RGBA'); d = ImageDraw.Draw(im)
        person(d, 520, 860, 1.25, (22, 26, 34, 255), cap=True)
        glow = 0.6 + 0.4 * math.sin(t * 2.3); r = 7 + 3 * glow
        d.ellipse([600 - r, 470 - r, 600 + r, 470 + r], fill=(255, int(120 + 60 * glow), 40, 255))
        sm = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sm)
        for k in range(6):
            ph = ((t * 0.35 + k / 6) % 1); sd.ellipse([600 + ph * 60 - 20 - ph * 30, 450 - ph * 320 - 20 - ph * 30, 600 + ph * 60 + 20 + ph * 30, 450 - ph * 320 + 20 + ph * 30], fill=(200, 200, 200, int(60 * (1 - ph))))
        im.alpha_composite(sm.filter(ImageFilter.GaussianBlur(10)))
        fg = Image.new('RGBA', im.size, (0, 0, 0, 0)); fd = ImageDraw.Draw(fg)
        for k in range(3):  # пробегающие люди на переднем плане
            ph = ((t - 25) * 0.45 + k * 0.37) % 1.4 - 0.2
            person(fd, int(-200 + ph * (SW + 400)), 1500, 2.4, (6, 7, 8, 235))
        im.alpha_composite(fg.filter(ImageFilter.GaussianBlur(9)))
        z = 1 + (t - 25) * 0.01; im = im.convert('RGB').resize((int(SW * z), int(SH * z))); dx = (im.width - SW) // 2
        return finish(im.crop((dx, dx, dx + SW, dx + SH)), t, shake=2.5)
    if t < 52:  # телефон
        im = YARD_BLUR.copy().convert('RGBA')
        mode = 'ring' if t < 39.4 else 'call' if t < 45.5 else 'end'
        ph = phone_screen(t, mode)
        vx = int(math.sin(t * 90) * 5) if mode == 'ring' and (t - 35.2) % 0.85 < 0.45 else 0
        dy = int(ease((t - 49.5) / 2.5) * 900)
        im.alpha_composite(ph, (140 + PAD + vx, 110 + PAD + dy))
        im = im.convert('RGB')
        if mode == 'end' and 45.5 < t < 46.3 and rng.random() < 0.6:  # глитч обрыва
            a = np.asarray(im).copy(); y0 = rng.integers(0, SH - 60); a[y0:y0 + 60] = np.roll(a[y0:y0 + 60], rng.integers(-60, 60), 1); im = Image.fromarray(a)
        return finish(im, t, shake=2.0)
    if t < 57.5:  # гриб над городом
        p = (t - 52) / 5.5; im = BG['nuke'].copy().convert('RGBA'); cl = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cl)
        cx, base = SW // 2 + 60, 1150; top = int(lerp(820, 380, ease(p))); w = lerp(60, 120, p)
        d.polygon([(cx - w * .5, base), (cx + w * .5, base), (cx + w * .3, top), (cx - w * .3, top)], fill=(120, 95, 80, 255))
        cr = lerp(120, 230, ease(p)); rs = np.random.default_rng(4)
        for k in range(26):
            a = rs.uniform(0, 2 * math.pi); rr = rs.uniform(0, 1) * cr; bx = cx + math.cos(a) * rr * 1.3; by = top + math.sin(a) * rr * 0.55
            r = rs.uniform(.35, .6) * cr; sh = int(rs.uniform(80, 140)); d.ellipse([bx - r, by - r * .8, bx + r, by + r * .8], fill=(sh + 20, sh, sh - 10, 255))
        d.ellipse([cx - cr * .9, top - cr * .1, cx + cr * .9, top + cr * .45], fill=(230, 140, 60, 140))
        im.alpha_composite(cl.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(NUKE_CITY)
        d = ImageDraw.Draw(im); person(d, SW // 2 - 230, SH + 120, 2.0, (5, 5, 6, 255))
        z = 1 + p * 0.06; im = im.convert('RGB').resize((int(SW * z), int(SH * z))); dx = (im.width - SW) // 2
        return finish(im.crop((dx, dx, dx + SW, dx + SH)), t, shake=1.2)
    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)  # титр
    if t > 58.0:
        a = int(255 * ease((t - 58.0) / 0.5))
        d.text((W / 2, H / 2 - 60), 'ГОРОД Z', font=font(84), fill=(a, int(a * .25), int(a * .2)), anchor='mm')
        d.text((W / 2, H / 2 + 30), '140 КИЛОМЕТРОВ', font=font(34), fill=(a, a, a), anchor='mm')
        d.text((W / 2, H / 2 + 120), 'Серия 1 из 8 · Продолжение следует…', font=font(26, False), fill=(int(a * .7),) * 3, anchor='mm')
    return im

if ONLY is not None:
    frame(ONLY).save(f'preview_{ONLY:05.1f}.jpg'); sys.exit()
ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                       '-shortest', '-movflags', '+faststart', 'Gorod_Z_seriya_1.mp4'], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    ff.stdin.write(frame(i / FPS).tobytes())
    if i % 240 == 0: print('t =', i / FPS, flush=True)
ff.stdin.close(); ff.wait()
