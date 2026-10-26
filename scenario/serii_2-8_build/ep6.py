"""Серия 6 «Железка»."""
from common import *

LINES = [
    (1.3, 'SEM', 'На счёт три.|Не оглядывайтесь.', '— На счёт три. Не оглядывайтесь.', None),
    (11.0, 'DIKTOR', 'Стоять!', '— Стоять!', 'mega'),
    (15.3, 'SEM', 'Карту держи!|Сосновка — красным крестиком!|Беги!', '— Карту держи! Сосновка — красным крестиком! Беги!', 'shout'),
    (22.4, 'HERO', 'Семёныч!', '— Семёныч!!', 'shout'),
    (36.0, 'N', 'Он знал, что так будет.|Он всё решил ещё вчера.', 'Он знал, что так будет. Он всё решил ещё вчера.', None),
    (46.3, 'DIKTOR', 'В зону строгого карантина включены населённые пункты:|Ольховка, Березняки, Сосновка.|Въезд и выезд запрещён.',
     '«…в зону строгого карантина включены: Ольховка, Березняки, Сосновка… Въезд и выезд запрещён.»', 'radio'),
]

def sfx():
    return [(0, crickets(8), .05), (0, drone(8, 50, 55), .15), (8, steps(7, 5), .45), (8, wind(15), .15),
            (25, steps(1.5, 5), .4), (26.5, thump(), .6), (29.0, gunshot(), .85), (35, crickets(10), .04),
            (45, birds(12.5), .08), (45.5, static(12), .06), (TITLE_T, bass_hit(), .95)]

def frame_factory(subs):
    rs = np.random.default_rng
    night = canvas((10, 14, 24), (16, 20, 26)); d = ImageDraw.Draw(night)
    d.rectangle([0, 900, SW, SH], fill=(10, 12, 12))
    for k in range(9):  # фермы моста
        x = 40 + k * 90; d.line([x, 900, x + 45, 640], fill=(30, 34, 40), width=6); d.line([x + 45, 640, x + 90, 900], fill=(30, 34, 40), width=6)
    d.line([0, 640, SW, 640], fill=(30, 34, 40), width=8); d.line([0, 900, SW, 900], fill=(40, 44, 50), width=10)
    d.rectangle([SW - 160, 520, SW - 60, 900], fill=(20, 22, 26))  # вышка
    forest = canvas((140, 150, 145), (70, 78, 70)); d = ImageDraw.Draw(forest)
    trees(d, rs(41), 1100, 26, 500, 900, (60, 70, 62)); trees(d, rs(42), 1250, 14, 450, 750, (30, 38, 32)); d.rectangle([0, 1200, SW, SH], fill=(40, 44, 36))

    def beam(im, t, ang):
        cone(im, SW - 110, 540, ang, 6, 1400, 120, (230, 230, 210)); glow(im, SW - 110, 540, 30, (255, 255, 230), 255)

    def frame(t):
        if t < 8:
            im = night.copy().convert('RGBA'); beam(im, t, 150 + 25 * math.sin(t * .8)); d = ImageDraw.Draw(im)
            for k in range(60): x = k * 14; d.line([x, SH, x + 10, SH - 260 - 40 * math.sin(k)], fill=(8, 12, 8), width=5)
            for k, c in enumerate([SEM_C, HERO_C, LENA_C, MASHA_C]): d.ellipse([140 + k * 140, 1120, 220 + k * 140, 1170], fill=c)
            return finish(im, t, subs)
        if t < 15:
            im = night.copy().convert('RGBA'); p = (t - 8) / 7; beam(im, t, lerp(140, 175, ease(p * 1.5))); d = ImageDraw.Draw(im)
            b = abs(math.sin(t * 10)) * 10
            for k, (c, kw) in enumerate([(SEM_C, {'cap': True}), (HERO_C, {}), (LENA_C, {'pony': True}), (MASHA_C, {'braids': True})]):
                person(d, int(100 + k * 120 + p * 250), int(900 - b), .55 if k < 3 else .38, c, **kw)
            return finish(im, t, subs, shake=3)
        if t < 25:
            im = night.copy().convert('RGBA'); beam(im, t, 168); d = ImageDraw.Draw(im); p = (t - 15) / 10
            person(d, int(lerp(260, 470, p)), 900, .6, SEM_C, cap=True, arms_up=t > 19)
            person(d, 120, 1500, 2.2, HERO_C)
            if t < 17.5: d.rectangle([330, 880, 400, 930], fill=(200, 190, 160))
            return finish(im, t, subs)
        if t < 35:
            im = Image.new('RGBA', (SW, SH), (6, 8, 12, 255)); d = ImageDraw.Draw(im)
            d.polygon([(0, 0), (SW, 0), (SW, 500), (0, 700)], fill=(14, 18, 28)); d.polygon([(0, 700), (SW, 500), (SW, SH), (0, SH)], fill=(10, 12, 10))
            if t < 27:
                q = ease((t - 25) / 1.6)
                for k, c in enumerate([HERO_C, LENA_C, MASHA_C]): person(d, 220 + k * 160, int(lerp(500, 1150, q)), .8 - k * .1, c)
            else:
                for k, c in enumerate([HERO_C, LENA_C, MASHA_C]): person(d, 220 + k * 160, 1150, .8 - k * .1, c)
            if 29 < t < 29.15: glow(im, 600, 300, 90, (255, 230, 150), 255)
            return finish(im, t, subs, shake=6 if 26.5 < t < 26.9 or 29 < t < 29.3 else .5)
        if t < 45:
            im = Image.new('RGBA', (SW, SH), (14, 18, 28, 255)); d = ImageDraw.Draw(im)
            d.polygon([(80, 360), (700, 300), (720, 1000), (60, 1060)], fill=(150, 150, 160))
            rs7 = np.random.default_rng(3)
            for k in range(10): d.line([rs7.uniform(80, 700), rs7.uniform(320, 1040), rs7.uniform(80, 700), rs7.uniform(320, 1040)], fill=(110, 110, 125), width=3)
            d.text((520, 520), '✕', font=font(90), fill=(170, 30, 30), anchor='mm'); d.text((520, 600), 'Сосновка', font=font(30), fill=(50, 50, 60), anchor='mm')
            for sx in (40, 690): d.ellipse([sx - 80, 900, sx + 80, 1100], fill=(30, 30, 34))
            return finish(zoom(im, 1 + (t - 35) * .02, .6, .4), t, subs, shake=1.5)
        if t < TITLE_T:
            im = forest.copy().convert('RGBA'); d = ImageDraw.Draw(im)
            d.rectangle([250, 1150, 500, 1240], fill=(60, 45, 30)); d.rounded_rectangle([290, 1020, 470, 1150], 10, fill=(40, 42, 40))
            d.ellipse([310, 1045, 390, 1125], fill=(20, 20, 20)); d.line([450, 1020, 520, 900], fill=(150, 150, 150), width=4)
            person(d, 620, 1400, 1.5, HERO_C); person(d, 120, 1420, 1.4, LENA_C, pony=True)
            return finish(zoom(im, 1 + (t - 45) * .012, .5, .8), t, subs)
        return title(t, 6)
    return frame

if __name__ == '__main__': run(6, LINES, sfx, frame_factory)
