"""Серия 8 «Сосновка» — финал сезона."""
from common import *

LINES = [
    (1.5, 'HERO', 'Тихо.|Уходим.|Сейчас.', '— Тихо. Уходим. Сейчас.', None),
    (11.0, 'N', 'Мы ушли за десять минут до них.', 'Мы ушли за десять минут до них.', None),
    (27.0, 'LENA', 'Здесь никого нет…', '— Здесь никого нет…', None),
    (41.0, 'MOM', 'Сынок…|Живой…|Я знала!|Я знала!', '— Сынок… Живой… Я знала! Я знала!', None),
    (49.9, 'HERO', 'Мам…|а где папа?', '— Мам… а где папа?', None),
    (52.2, 'MOM', 'Он поехал за вами в город.|По трассе.|Четыре дня назад.', '— Он поехал за вами в город. По трассе. Четыре дня назад.', None),
    (58.1, 'N', 'Мне придётся вернуться.', 'Мне придётся вернуться.', None),
]

def sfx():
    return [(0, room(7), .05), (0.5, creak(1.2), .12), (4.5, creak(1), .1), (7, engine(10), .3), (9, dogs(5), .2), (7, birds(10), .05),
            (17, wind(16), .3), (25.5, creak(3), .2), (33, steps(2.5, 4), .4), (35.5, boards(), .5), (36.6, boards(), .5), (37.8, boards(), .5),
            (40, hug_music(10), .12), (40, fire(17), .04), (TITLE_T, bass_hit(), .95)]

def frame_factory(subs):
    rs = np.random.default_rng
    dawn = canvas((120, 115, 105), (70, 74, 66)); d = ImageDraw.Draw(dawn)
    trees(d, rs(61), 1000, 30, 400, 800, (70, 78, 68)); d.rectangle([0, 950, SW, SH], fill=(55, 60, 48))
    village = canvas((130, 125, 115), (80, 84, 74)); d = ImageDraw.Draw(village)
    trees(d, rs(62), 640, 40, 150, 300, (70, 78, 68)); d.rectangle([0, 620, SW, SH], fill=(78, 84, 66))
    rs8 = rs(63)
    for k in range(12):
        x, y, s = rs8.uniform(20, SW - 120), rs8.uniform(680, 980), rs8.uniform(.6, 1.1)
        d.rectangle([x, y, x + 110 * s, y + 70 * s], fill=(70, 55, 40)); d.polygon([(x - 10 * s, y), (x + 120 * s, y), (x + 55 * s, y - 50 * s)], fill=(55, 50, 48))
        d.rectangle([x + 40 * s, y + 20 * s, x + 65 * s, y + 45 * s], fill=(30, 28, 25))
    d.line([0, 1000, SW, 940], fill=(95, 90, 75), width=30)
    trees(d, rs(64), 1350, 5, 1100, 1500, (25, 30, 25))
    house = canvas((125, 120, 110), (80, 82, 72)); d = ImageDraw.Draw(house)
    d.rectangle([60, 450, 560, 900], fill=(80, 60, 42)); d.polygon([(30, 450), (590, 450), (310, 220)], fill=(60, 55, 52))
    for x in (130, 380):
        d.rectangle([x, 560, x + 110, 680], fill=(25, 22, 20))
        for k in range(3): d.line([x - 10, 575 + k * 40, x + 120, 565 + k * 40], fill=(150, 130, 100), width=12)
    d.rectangle([0, 900, SW, SH], fill=(70, 74, 52))
    for x in range(0, SW, 40): d.rectangle([x, 1000, x + 18, 1040], fill=(60, 64, 44))

    def frame(t):
        if t < 7:
            im = Image.new('RGBA', (SW, SH), (14, 10, 7, 255)); glow(im, 600, 600, 90, (255, 170, 80), 70); d = ImageDraw.Draw(im)
            person(d, 620, 1250, 1.1, MIKH_C); d.rectangle([700, 760, 740, 860], fill=(25, 25, 25))
            person(d, 200, 1700, 2.6, HERO_C); d.ellipse([280, 1150, 600, 1260], fill=LENA_C)
            if t > 4: d.rounded_rectangle([60, 1000, 220, 1160], 30, fill=(40, 46, 30))
            return finish(im, t, subs, warm=True, dark=.25)
        if t < 17:
            im = dawn.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = (t - 7) / 10
            for k in range(3):
                x = lerp(-300, SW + 300, p * 1.3 - k * .25); car(d, x, 880, (20, 22, 20), 1.0); glow(im, x + 200, 920, 40, (255, 240, 200), 160)
            d = ImageDraw.Draw(im); d.polygon([(0, 1050), (SW, 1000), (SW, SH), (0, SH)], fill=(30, 34, 26))
            for k, (c, kw) in enumerate([(HERO_C, {}), (LENA_C, {'pony': True}), (MASHA_C, {'braids': True})]): person(d, 230 + k * 170, 1450, 1.2 - k * .15, c, **kw)
            return finish(im, t, subs, shake=1)
        if t < 25:
            im = village.copy().convert('RGBA'); d = ImageDraw.Draw(im)
            for k, (c, kw) in enumerate([(HERO_C, {}), (LENA_C, {'pony': True}), (MASHA_C, {'braids': True})]): person(d, 200 + k * 140, 1400, 1.5 - k * .2, c, **kw)
            return finish(zoom(im, 1 + (t - 17) * .012, .5, .4), t, subs)
        if t < 33:
            im = canvas((90, 90, 85), (60, 60, 55)).convert('RGBA'); d = ImageDraw.Draw(im)
            for x in range(80, 700, 60): d.rectangle([x, 300, x + 52, 1150], fill=(95, 78, 58)); d.line([x + 10, 320, x + 10, 1130], fill=(80, 64, 48), width=3)
            d.text((390, 620), 'ЗАРАЖЕНО.', font=font(84), fill=(170, 25, 20), anchor='mm'); d.text((390, 740), 'НЕ ВХОДИТЬ', font=font(70), fill=(170, 25, 20), anchor='mm')
            return finish(zoom(im, 1 + (t - 25) * .02), t, subs, shake=.6)
        if t < 40:
            im = house.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = ease((t - 33) / 2.5)
            d.rectangle([520, 1080, 760, 1160], fill=(60, 45, 30))
            nb = 3 - sum(t > x for x in (35.5, 36.6, 37.8))
            for k in range(nb): d.line([510, 1095 + k * 25, 770, 1100 + k * 25], fill=(150, 130, 100), width=14)
            person(d, int(lerp(100, 520, p)), 1200, 1.1, HERO_C)
            return finish(im, t, subs, shake=2 if t > 35 else .8)
        if t < 50:
            im = Image.new('RGBA', (SW, SH), (22, 15, 10, 255)); glow(im, 600, 600, 380, (255, 170, 80), 140); glow(im, 600, 600, 50, (255, 230, 150), 255); d = ImageDraw.Draw(im)
            for y in range(0, SH, 80): d.line([0, y, 150, y + 20], fill=(40, 30, 22), width=8)
            person(d, 330, 1450, 1.9, MOM_C, bun=True); person(d, 460, 1480, 2.0, HERO_C)
            return finish(zoom(im, 1 + (t - 40) * .008), t, subs, warm=True)
        if t < TITLE_T:
            im = Image.new('RGBA', (SW, SH), (22, 15, 10, 255)); glow(im, 650, 500, 380, (255, 170, 80), 130); d = ImageDraw.Draw(im)
            if t < 52.1: person(d, 400, 2450, 5.0, HERO_C)
            else: person(d, 380, 2450, 5.0, MOM_C, bun=True)
            return finish(zoom(im, 1 + (t - 50) * .012), t, subs, warm=True, dark=ease((t - 55.5) / 2) * .6)
        return title(t, 8, sub='Конец первого сезона')
    return frame

if __name__ == '__main__': run(8, LINES, sfx, frame_factory)
