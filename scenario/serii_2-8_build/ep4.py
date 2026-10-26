"""Серия 4 «Тоннель»."""
from common import *

LINES = [
    (0.8, 'N', 'Кровь была свежая.', 'Кровь была свежая.', None),
    (15.4, 'LENA', 'Я же говорила, что тут ребёнок!|Её зовут Маша.|Её мама… не дошла.', '— Я же говорила, что тут ребёнок! Её зовут Маша. Её мама… не дошла.', None),
    (25.8, 'MASHA', 'Он сказал…|что мы бесполезные.', '— Он сказал… что мы бесполезные.', None),
    (33.3, 'N', 'Тогда я впервые захотел кого-то убить.', 'Тогда я впервые захотел кого-то убить.', None),
    (40.0, 'SEM', 'Завалило.|Взрывной волной.', '— Завалило. Взрывной волной.', 'echo'),
    (48.5, 'GLEB', 'Аптечку-то верните.|И девчонку тоже.|Она нам должна.', '— Аптечку-то верните. И девчонку тоже. Она нам должна.', 'echo'),
]

def sfx():
    ev = [(0, room(57.5), .07), (0, heartbeat(6, 95), .2), (6, steps(9, 1.8), .3), (12, steps(3, 1.8), .15),
          (38.6, thump(), .6), (38.9, thump(), .4), (44.5, steps(13, 2.2), .25), (52, drone(5.5, 40, 50), .3), (TITLE_T, bass_hit(), .95)]
    for k in np.arange(0.5, 57, 2.1): ev.append((float(k), drip(), .12))
    return ev

def frame_factory(subs):
    def tunnel(blocked=False):
        im = Image.new('RGB', (SW, SH), (6, 7, 7)); d = ImageDraw.Draw(im); cx, cy = SW // 2, 640
        for k in range(14, 0, -1):
            s = k / 14; w, h = 380 * s, 560 * s; c = int(8 + 34 * s)
            d.rectangle([cx - w, cy - h, cx + w, cy + h * 1.1], fill=(c, c + 2, c))
        d.polygon([(0, SH), (SW, SH), (cx + 30, cy + 40), (cx - 30, cy + 40)], fill=(30, 31, 29))
        for sx in (-1, 1):
            for off in (0, 30): d.line([cx + sx * 30, cy - 20 - off, sx * (SW // 2 + 10) + cx, 350 - off * 3], fill=(26, 24, 20), width=8)
        if blocked:
            d.polygon([(cx - 120, cy + 50), (cx - 60, cy - 120), (cx + 40, cy - 90), (cx + 130, cy + 50)], fill=(80, 78, 72))
            d.polygon([(cx - 140, cy + 60), (cx + 10, cy - 30), (cx + 150, cy + 60)], fill=(95, 92, 85))
            for k in range(6): d.line([cx - 80 + k * 30, cy - 60, cx - 60 + k * 35, cy - 160], fill=(60, 40, 30), width=4)
        return im
    T, TB = tunnel(), tunnel(True)

    def frame(t):
        if t < 6:
            im = T.copy().convert('RGBA'); d = ImageDraw.Draw(im); sx = 380 + 200 * math.sin(t * .6)
            d.rounded_rectangle([330, 1000, 470, 1050], 20, fill=(200, 195, 185)); d.ellipse([390, 990, 520, 1060], fill=(120, 20, 15))
            cone(im, SW // 2, SH + 100, -90 + (sx - 380) / 20, 12, 900, 140)
            return finish(im, t, subs, dark=.2, shake=1.2)
        if t < 15:
            im = T.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = (t - 6) / 9
            person(d, 300, int(1250 - p * 200), 1.0 - p * .4, HERO_C, light=(255, 240, 200)); person(d, 470, int(1260 - p * 200), 1.0 - p * .4, SEM_C, cap=True, light=(255, 240, 200))
            cone(im, 360, 1000 - p * 150, -95, 10, 700, 90); cone(im, 530, 1000 - p * 150, -85, 10, 700, 90)
            return finish(im, t, subs, dark=.15, shake=1)
        if t < 25:
            im = Image.new('RGBA', (SW, SH), (8, 8, 8, 255)); d = ImageDraw.Draw(im)
            d.rectangle([60, 300, SW - 60, SH - 150], fill=(34, 34, 30)); glow(im, 380, 760, 340, (230, 220, 180), 70)
            person(d, 260, 1180, 1.25, LENA_C, pony=True); person(d, 500, 1180, .8, MASHA_C, braids=True)
            d.rectangle([470, 960, 520, 990], fill=(220, 220, 210))
            return finish(im, t, subs, warm=True)
        if t < 33:
            im = Image.new('RGBA', (SW, SH), (10, 10, 10, 255)); glow(im, 400, 800, 400, (200, 190, 160), 60); d = ImageDraw.Draw(im)
            person(d, 400, 2300, 4.2, MASHA_C, braids=True)
            d.ellipse([330, 860, 360, 890], fill=(200, 200, 220)) if int(t * 2) % 5 else None
            return finish(zoom(im, 1 + (t - 25) * .01), t, subs, warm=True)
        if t < 45:
            im = TB.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = ease((t - 33) / 5)
            cone(im, SW // 2, SH, -90, 14, 900, 120)
            person(d, 220, 1320, 1.2, SEM_C, cap=True, light=(255, 240, 200)); person(d, 560, 1300, 1.1, LENA_C, pony=True); person(d, 450, 1310, .7, MASHA_C, braids=True)
            return finish(zoom(im, 1 + p * .1), t, subs, dark=.15, shake=4 if 38.6 < t < 39.3 else 1)
        if t < TITLE_T:
            im = T.copy().convert('RGBA'); p = ease((t - 45) / 12)
            for k, x in enumerate((300, 360, 440, 500)):
                y = lerp(620, 900, p) + k * 6; cone(im, x + k * 5, y, -90 + 180 * 0 + 90 + (k - 1.5) * 8, 9, 600 + p * 300, 70)
                glow(im, x, y, 26 + p * 30, (255, 240, 200), 230)
            d = ImageDraw.Draw(im)
            if p > .45: person(d, 380, int(lerp(700, 1300, p)), lerp(.3, 1.3, p), GLEB_C, bulky=True, light=(255, 240, 200))
            return finish(im, t, subs, dark=.1, shake=1.5)
        return title(t, 4)
    return frame

if __name__ == '__main__': run(4, LINES, sfx, frame_factory)
