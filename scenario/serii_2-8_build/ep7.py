"""Серия 7 «Охотник»."""
from common import *

LINES = [
    (1.0, 'LENA', 'Она горит!|У неё температура под сорок!', '— Она горит! У неё температура под сорок!', 'shout'),
    (6.6, 'N', 'Третьи сутки.|Сорок километров до Сосновки.|И ни одного шанса.', 'Третьи сутки. 40 километров до Сосновки. И ни одного шанса.', None),
    (17.0, 'MIKH', 'Не бойтесь.|Одни в лесу?|Пойдёмте, девчонку подлечим.', '— Не бойтесь. Одни в лесу? Пойдёмте, девчонку подлечим.', None),
    (26.5, 'N', 'Впервые за три дня я поверил, что всё будет хорошо.', 'Впервые за три дня я поверил, что всё будет хорошо.', None),
    (48.6, 'MIKH', 'Трое.|Девчонка мелкая.|Таблетки йода есть, патронов нет.|Приезжайте к утру.|Заберёте.',
     '— Трое. Девчонка мелкая. Таблетки йода есть, патронов нет. Приезжайте к утру. Заберёте.', 'radio'),
]

def sfx():
    return [(0, wind(6), .15), (0.6, thump(), .35), (6, rain(10), .3), (6, steps(10, 1.6), .2), (16, rain(9), .12),
            (16.3, steps(1.5, 2.5), .3), (25, fire(17), .25), (25, hug_music(10), .05), (42, room(15.5), .05),
            (42.5, crickets(15), .03), (47.8, static(9.5), .05), (TITLE_T, bass_hit(), .95)]

def frame_factory(subs):
    rs = np.random.default_rng
    fog = canvas((120, 128, 126), (80, 86, 82)); d = ImageDraw.Draw(fog)
    trees(d, rs(51), 1000, 30, 500, 800, (95, 102, 98)); trees(d, rs(52), 1150, 18, 450, 700, (60, 66, 62)); d.rectangle([0, 1100, SW, SH], fill=(55, 58, 52))
    fog = Image.blend(fog, Image.new('RGB', fog.size, (130, 135, 132)), .25)
    wet = canvas((70, 78, 76), (40, 44, 40)); d = ImageDraw.Draw(wet)
    trees(d, rs(53), 1050, 30, 500, 900, (45, 52, 48)); trees(d, rs(54), 1200, 14, 450, 750, (25, 30, 27)); d.rectangle([0, 1180, SW, SH], fill=(35, 38, 32))
    cabin = canvas((70, 48, 30), (40, 28, 18)); d = ImageDraw.Draw(cabin)
    for y in range(0, SH, 60): d.line([0, y, SW, y], fill=(52, 36, 22), width=6)
    d.rectangle([420, 600, 720, 1100], fill=(60, 58, 55)); d.rectangle([470, 820, 670, 980], fill=(20, 12, 8))
    d.rectangle([40, 950, 400, 980], fill=(80, 56, 34)); d.rectangle([60, 980, 80, 1200], fill=(70, 48, 30)); d.rectangle([360, 980, 380, 1200], fill=(70, 48, 30))
    d.rectangle([0, 1200, SW, SH], fill=(46, 32, 20))

    def stove(im, t, a=1.0):
        fl = .8 + .2 * math.sin(t * 17) * math.sin(t * 5.3)
        glow(im, 570, 900, int(300 * fl), (255, 120, 30), int(120 * a)); glow(im, 570, 900, 70, (255, 200, 90), int(240 * a * fl))

    def frame(t):
        if t < 6:
            im = fog.copy().convert('RGBA'); d = ImageDraw.Draw(im); q = ease((t - .4) / .5)
            person(d, 380, 1230, 1.0, LENA_C, pony=True)
            if t < .4: person(d, 560, 1230, .65, MASHA_C, braids=True)
            else: d.ellipse([480, 1190, 680, 1240], fill=MASHA_C)
            return finish(im, t, subs, shake=1.5 if t < 1 else .5)
        if t < 16:
            im = wet.copy().convert('RGBA'); d = ImageDraw.Draw(im); b = abs(math.sin(t * 3)) * 12
            person(d, 360, int(1350 - b), 1.4, HERO_C); d.ellipse([230, int(820 - b), 490, int(920 - b)], fill=MASHA_C)
            person(d, 620, int(1300 - b), 1.1, LENA_C, pony=True)
            particles(im, t, 300, (170, 180, 190), 1600, 0, 9, drift=-60, streak=40)
            return finish(im, t, subs, shake=1.2)
        if t < 25:
            im = wet.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = ease((t - 16) / 1.6)
            person(d, int(lerp(820, 470, p)), 1350, 1.5, MIKH_C, gun=True)
            d.polygon([(380, 820), (560, 820), (520, 860), (420, 860)], fill=(70, 70, 70))  # усы-силуэт шапки
            particles(im, t, 150, (170, 180, 190), 1600, 0, 9, drift=-60, streak=40)
            return finish(im, t, subs)
        if t < 35:
            im = cabin.copy().convert('RGBA'); stove(im, t); d = ImageDraw.Draw(im)
            for k, x in enumerate((110, 250)): d.ellipse([x, 920, x + 90, 950], fill=(200, 190, 170)); glow(im, x + 45, 900 - (t * 30 + k * 40) % 120, 20, (220, 220, 220), 40)
            person(d, 120, 1400, 1.2, LENA_C, pony=True); d.rounded_rectangle([200, 1080, 380, 1200], 30, fill=(110, 90, 60))
            return finish(im, t, subs, warm=True)
        if t < 42:
            im = cabin.copy().convert('RGBA'); stove(im, t, .8); d = ImageDraw.Draw(im)
            person(d, 360, 1750, 3.0, HERO_C)
            return finish(zoom(im, 1 + (t - 35) * .01), t, subs, warm=True, dark=ease((t - 38) / 4) * .5)
        if t < 48:
            im = Image.new('RGBA', (SW, SH), (6, 5, 4, 255)); d = ImageDraw.Draw(im)
            w = lerp(6, 18, ease((t - 44) / 3)); glow(im, 400, 700, 60, (255, 180, 90), 120)
            d.rectangle([400 - w, 200, 400 + w, 1200], fill=(220, 160, 90))
            person(d, 230, 1900, 3.2, HERO_C)
            return finish(im, t, subs, warm=True)
        if t < TITLE_T:
            im = Image.new('RGBA', (SW, SH), (4, 3, 2, 255)); inner = Image.new('RGBA', (SW, SH), (60, 40, 22, 255)); d = ImageDraw.Draw(inner)
            glow(inner, 520, 640, 200, (255, 190, 100), 180); d = ImageDraw.Draw(inner)
            d.rectangle([150, 820, 700, 860], fill=(80, 56, 34)); d.rounded_rectangle([200, 700, 320, 820], 20, fill=(40, 46, 30)); d.rounded_rectangle([340, 690, 450, 820], 20, fill=(20, 20, 22))
            person(d, 560, 1250, 1.3, MIKH_C); d.rectangle([600, 760, 640, 860], fill=(30, 30, 30)); d.line([620, 760, 640, 690], fill=(30, 30, 30), width=4)
            m = Image.new('L', (SW, SH), 0); ImageDraw.Draw(m).rectangle([180, 0, 620, SH], fill=255)
            im = Image.composite(inner, im, m.filter(ImageFilter.GaussianBlur(8)))
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 180, SH], fill=(20, 14, 8)); d.rectangle([620, 0, SW, SH], fill=(20, 14, 8))
            return finish(zoom(im, 1 + (t - 48) * .015), t, subs, warm=True)
        return title(t, 7)
    return frame

if __name__ == '__main__': run(7, LINES, sfx, frame_factory)
