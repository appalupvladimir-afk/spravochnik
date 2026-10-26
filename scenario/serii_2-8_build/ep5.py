"""Серия 5 «Оцепление»."""
from common import *

LINES = [
    (0.8, 'SEM', 'Вентиляционная шахта!|Слева!|Лезьте!', '— Вентиляционная шахта! Слева! Лезьте!', 'shout'),
    (14.5, 'N', 'Мы выбрались.|Но город ещё не отпустил нас.', 'Мы выбрались. Но город ещё не отпустил нас.', None),
    (20.6, 'DIKTOR', 'Внимание!|Выезд из города запрещён!|Возвращайтесь в укрытия!', 'Внимание! Выезд из города запрещён! Возвращайтесь в укрытия!', 'mega'),
    (35.0, 'LENA', 'Нас отсюда не выпустят.|Никого не выпустят.', '— Нас отсюда не выпустят. Никого не выпустят.', None),
    (47.3, 'SEM', 'Слушай внимательно, сынок.|Я дальше железнодорожного моста не дойду.|Я хватанул дозу ещё в первый день.',
     '— Слушай внимательно, сынок. Я дальше железнодорожного моста не дойду. Я хватанул дозу ещё в первый день.', None),
]

def sfx():
    return [(0, whoosh(), .7), (0, fire(6), .5), (0.3, crowd(3), .3), (6, scrape(8), .2), (6, room(51), .05),
            (13.6, clang(1.5), .25), (14, wind(6), .2), (20, engine(10), .12), (20, crowd(20), .3),
            (31.0, gunshot(), .6), (31.6, gunshot(), .55), (33.0, gunshot(), .6), (40, geiger(7, 4, 8), .15),
            (40, heartbeat(17.5, 60), .12), (47, wind(10.5), .12), (TITLE_T, bass_hit(), .95)]

def frame_factory(subs):
    rs = np.random.default_rng
    dawn = canvas((110, 100, 95), (60, 62, 60)); d = ImageDraw.Draw(dawn)
    city(d, SW, 760, rs(31), (40, 40, 42), .0, .6); d.rectangle([0, 760, SW, SH], fill=(52, 50, 44))
    for k in range(3): d.ellipse([100 + k * 220, 450, 260 + k * 220, 700], fill=(70, 66, 64))
    chk = canvas((95, 92, 88), (58, 58, 56)); d = ImageDraw.Draw(chk)
    city(d, SW, 720, rs(33), (48, 48, 50), .0, .5); d.rectangle([0, 720, SW, SH], fill=(55, 54, 50))
    d.polygon([(200, 820), (560, 820), (600, 760), (520, 740), (520, 700), (330, 700), (300, 740), (160, 760)], fill=(30, 34, 28))  # БТР
    d.rectangle([420, 670, 600, 690], fill=(30, 34, 28))
    for x in range(200, 600, 70): d.ellipse([x, 800, x + 55, 855], fill=(12, 12, 12))
    for x in range(0, SW, 140): d.rectangle([x, 860, x + 110, 930], fill=(110, 108, 100))
    for x in range(0, SW, 12): d.line([x, 840 + 6 * math.sin(x), x + 12, 846 - 6 * math.sin(x)], fill=(40, 40, 40), width=2)
    for x in (100, 330, 620): person(d, x, 860, .55, SOLD_C, gun=True)

    def frame(t):
        if t < 6:
            im = Image.new('RGBA', (SW, SH), (10, 8, 6, 255)); p = ease(t / .6)
            glow(im, SW // 2, 700, int(150 + 350 * p), (255, 140, 40), int(230 - t * 15)); glow(im, SW // 2, 700, int(80 + 120 * p), (255, 220, 120), 220)
            d = ImageDraw.Draw(im); person(d, 230, 1600, 2.4, SEM_C, cap=True); d.line([340, 900, 160, 650], fill=SEM_C, width=40)
            return finish(im, t, subs, shake=6 * max(.2, 1 - t / 3), warm=True)
        if t < 14:
            im = Image.new('RGBA', (SW, SH), (5, 5, 5, 255)); d = ImageDraw.Draw(im); cx, cy = SW // 2, 620
            for k in range(12, 0, -1):
                s = k / 12; w = 380 * s; c = int(10 + 50 * s); d.rectangle([cx - w, cy - w, cx + w, cy + w], outline=(c, c, c + 3), width=int(20 * s))
            q = (t - 6) / 8; person(d, cx, int(lerp(900, 760, q)), .5 - q * .2, MASHA_C, braids=True); person(d, cx, int(lerp(1150, 900, q)), .9 - q * .3, LENA_C, pony=True)
            return finish(im, t, subs, dark=.2, shake=1)
        if t < 20:
            im = dawn.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = ease((t - 14) / 4)
            d.rectangle([180, 1050, 600, 1110], fill=(25, 25, 25))
            for k in range(3): person(d, 250 + k * 150, int(1100 - p * 60 * (k + 1) / 3), .9 - k * .1, [MASHA_C, LENA_C, SEM_C][k], braids=k == 0, pony=k == 1, cap=k == 2)
            return finish(im, t, subs)
        if t < 30:
            im = chk.copy().convert('RGBA')
            return finish(zoom(im, 1 + (t - 20) * .015, .5, .6), t, subs)
        if t < 40:
            im = chk.copy().convert('RGBA'); d = ImageDraw.Draw(im); rs5 = np.random.default_rng(int(t * 3))
            for k in range(22):
                x = (k * 47 + (t - 30) * (20 if k % 2 else -40)) % SW; person(d, x, 1150 + (k % 4) * 60, .9 + (k % 4) * .12, (14 + k % 3, 14, 14))
            for st in (31.0, 31.6, 33.0):
                if st < t < st + .12: glow(im, 330, 720, 60, (255, 230, 150), 255)
            return finish(im, t, subs, shake=5 if any(st < t < st + .3 for st in (31.0, 31.6, 33.0)) else 2)
        if t < 47:
            im = Image.new('RGBA', (SW, SH), (40, 40, 42, 255)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([-40, 450, SW + 40, 800], 120, fill=(170, 130, 110)); d.rectangle([-40, 380, 200, 870], fill=SEM_C)
            rs6 = np.random.default_rng(6)
            for k in range(9):
                x, y, r = rs6.uniform(260, SW - 30), rs6.uniform(510, 740), rs6.uniform(18, 50)
                d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(140, 50, 45)); d.ellipse([x - r * .4, y - r * .3, x + r * .4, y + r * .3], fill=(90, 40, 40))
            return finish(zoom(im, 1 + (t - 40) * .02), t, subs, warm=True)
        if t < TITLE_T:
            im = Image.new('RGBA', (SW, SH), (60, 62, 60, 255)); glow(im, 600, 400, 400, (150, 140, 120), 120); d = ImageDraw.Draw(im)
            person(d, 380, 2500, 5.0, SEM_C, cap=True)
            d.polygon([(280, 1110), (480, 1110), (430, 1250), (330, 1250)], fill=(60, 60, 64))  # борода
            return finish(zoom(im, 1 + (t - 47) * .01), t, subs)
        return title(t, 5)
    return frame

if __name__ == '__main__': run(5, LINES, sfx, frame_factory)
