"""Серия 2 «Ветер»."""
from common import *

LINES = [
    (0.4, 'N', 'Через сорок минут мы проехали ровно триста метров.', 'Через сорок минут мы проехали ровно триста метров.', None),
    (15.2, 'SEM', 'По трассе не пройдёте.|Там пробка до кольцевой.|Пойдём железкой.|Я дорогу знаю.', '— По трассе не пройдёте. Там пробка до кольцевой. Пойдём железкой. Я дорогу знаю.', None),
    (23.0, 'N', 'Он служил в химвойсках.|Тогда я ещё не знал, как нам повезло.', 'Он служил в химвойсках. Тогда я ещё не знал, как нам повезло.', None),
    (34.5, 'LENA', 'Она же… к нам идёт?', '— Она же… к нам идёт?', None),
    (50.0, 'SEM', 'Два часа!|У нас два часа, чтобы найти подвал!|Бежим!', '— Два часа! У нас два часа, чтобы найти подвал! Бежим!', 'shout'),
]

def sfx():
    return [
        (0, room(57.5), .05), (0, engine(7), .18), (0.5, crowd(14), .18), (2.5, siren(20), .03),
        (3.2, norm(hp(noise(.4), 2000)) * np.exp(-tt(.4) / .08), .25),  # разбитое стекло
        (7.2, steps(1.2, 3), .3), (9.0, knock(), .5), (9.35, knock(), .5), (9.7, knock(), .5),
        (16, steps(6, 2), .15), (22, geiger(18, 1.5, 4), .12), (30, wind(10), .35), (40, geiger(10, 6, 60), .35),
        (50, geiger(7.5, 60, 80), .25), (50, steps(7.5, 4.5), .4), (50, wind(7.5), .25), (TITLE_T, bass_hit(), .95),
    ]

def frame_factory(subs):
    rs = np.random.default_rng
    yard = canvas((90, 80, 70), (55, 58, 60)); d = ImageDraw.Draw(yard)
    city(d, SW, 900, rs(5), (40, 40, 42), .04, .9); city(d, SW, 980, rs(6), (22, 24, 26), .08, 1.4); d.rectangle([0, 980, SW, SH], fill=(30, 31, 32))
    # пробка: вид через лобовое стекло
    traffic = canvas((95, 90, 85), (60, 60, 62)); d = ImageDraw.Draw(traffic)
    city(d, SW, 800, rs(8), (35, 36, 38), .05, 1.0); d.polygon([(0, SH), (SW, SH), (500, 760), (300, 760)], fill=(42, 42, 44))
    for i, (x, y, s) in enumerate([(300, 760, .5), (420, 770, .55), (180, 790, .7), (480, 810, .8), (90, 850, 1.0), (430, 880, 1.1)]):
        car(d, x, y, (18, 18, 20), s, tail=True)
    # мост
    bridge = canvas((60, 60, 62), (95, 92, 85)); d = ImageDraw.Draw(bridge)
    city(d, SW, 700, rs(12), (32, 34, 36), .03, .7); d.rectangle([0, 700, SW, SH], fill=(48, 55, 58))
    d.polygon([(0, 1000), (SW, 900), (SW, 960), (0, 1080)], fill=(70, 70, 68))
    for k in range(9): x = k * 100; d.line([x, 1000 - x * .11, x, 920 - x * .11], fill=(40, 40, 40), width=5)
    d.line([0, 920, SW, 820], fill=(40, 40, 40), width=6)
    gauge_bg = canvas((40, 40, 38), (25, 25, 24))

    def gauge(im, val, cx=SW // 2, cy=560, r=230):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([cx - 300, cy - 300, cx + 300, cy + 420], 40, fill=(70, 72, 60)); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(215, 210, 190))
        d.pieslice([cx - r + 20, cy - r + 20, cx + r - 20, cy + r - 20], -40, -15, fill=(200, 60, 50))
        for k in range(11):
            a = math.radians(-165 + k * 15); d.line([cx + math.cos(a) * (r - 20), cy + math.sin(a) * (r - 20), cx + math.cos(a) * (r - 50), cy + math.sin(a) * (r - 50)], fill=(30, 30, 30), width=4)
        a = math.radians(-165 + 150 * val); d.line([cx, cy, cx + math.cos(a) * (r - 40), cy + math.sin(a) * (r - 40)], fill=(20, 20, 20), width=7)
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(20, 20, 20)); d.text((cx, cy + 120), 'СОСНА', font=font(40), fill=(40, 40, 30), anchor='mm')
        d.text((cx, cy + 300), 'мкЗв/ч', font=font(30, False), fill=(200, 200, 180), anchor='mm')

    def frame(t):
        if t < 7:
            im = traffic.copy().convert('RGBA'); d = ImageDraw.Draw(im)
            for k in range(4):  # бегущие по обочине
                x = (t * 160 + k * 230) % (SW + 200) - 100; person(d, SW - 40 - (x * .25), 1000 - k * 8, .45 + .05 * k, (15, 15, 16))
            d.rectangle([0, 1180, SW, SH], fill=(8, 8, 9)); d.ellipse([60, 1060, 330, 1340], outline=(20, 20, 22), width=26)  # руль
            person(d, 560, 1600, 1.4, (55, 15, 14), pony=True)
            if 3.2 < t < 3.6: glow(im, 200, 860, 80, (255, 255, 255), 120)
            return finish(zoom(im, 1 + t * .006), t, subs, shake=1.5)
        if t < 15:
            im = yard.copy().convert('RGBA'); d = ImageDraw.Draw(im); car(d, 60, 1060, s=1.6)
            person(d, 520, 1270, 1.0, HERO_C); person(d, 640, 1260, .9, LENA_C, pony=True)
            d.rectangle([350, 1080, 400, 1150], fill=(140, 30, 25))  # канистра
            if t > 8.6:
                p = ease((t - 8.6) / 1.2); person(d, int(lerp(-150, 260, p)), 1250, 1.05, SEM_C, cap=True)
            return finish(im, t, subs, shake=1.0)
        if t < 22:
            im = zoom(yard, 1.6, .5, .8).convert('RGBA'); d = ImageDraw.Draw(im)
            person(d, 380, 1900, 3.0, SEM_C, cap=True)
            d.line([480, 1150, 700, 1000 - 30 * math.sin(t)], fill=SEM_C, width=40)
            return finish(im, t, subs, shake=1.2)
        if t < 30:
            im = gauge_bg.copy(); d = ImageDraw.Draw(im)
            if t < 26:
                gauge(im, .12 + .03 * math.sin(t * 7))
            else:
                d.rectangle([60, 200, SW - 60, SH - 200], fill=(200, 190, 160))
                rs2 = np.random.default_rng(2)
                for k in range(14): d.line([rs2.uniform(60, SW - 60), rs2.uniform(200, SH - 200), rs2.uniform(60, SW - 60), rs2.uniform(200, SH - 200)], fill=(150, 140, 110), width=3)
                d.line([60, 700, SW - 60, 640], fill=(80, 100, 150), width=14)  # река
                pts = [(220, 1050), (300, 900), (420, 780), (520, 560), (600, 380)]
                p = ease((t - 26.3) / 3); n = int(1 + p * (len(pts) - 1))
                d.line(pts[:max(2, n)], fill=(40, 40, 40), width=6)
                d.text((600, 340), 'Сосновка', font=font(30), fill=(60, 50, 40), anchor='mm')
            return finish(im, t, subs)
        if t < 40:
            p = (t - 30) / 10; im = bridge.copy().convert('RGBA'); cl = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cl)
            rs3 = np.random.default_rng(4)
            for k in range(30):
                x = rs3.uniform(-100, SW * (0.4 + p * .7)); y = rs3.uniform(100, 600); r = rs3.uniform(90, 200)
                d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(15, 15, 17, 235))
            im.alpha_composite(cl.filter(ImageFilter.GaussianBlur(20))); d = ImageDraw.Draw(im)
            for k, (c, kw) in enumerate([(SEM_C, {'cap': True}), (HERO_C, {}), (LENA_C, {'pony': True})]):
                x = 380 + k * 70 + (t - 30) * 8; person(d, x, int(960 - x * .11), .32, c, **kw)
            return finish(im, t, subs)
        if t < 50:
            im = gauge_bg.copy(); v = min(.95, .2 + ease((t - 40) / 8) * .8 + .02 * math.sin(t * 40)); gauge(im, v)
            if t > 46:
                ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rectangle([0, 0, SW, SH], fill=(120, 0, 0, int(40 * (1 + math.sin(t * 12)))))
                im = Image.alpha_composite(im.convert('RGBA'), ov)
            return finish(zoom(im, 1 + (t - 40) * .02), t, subs, shake=1 + (t - 40) * .3)
        if t < TITLE_T:
            im = yard.copy().convert('RGBA'); cl = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(cl)
            d.rectangle([0, 0, SW, 520], fill=(10, 10, 12, 220)); im.alpha_composite(cl.filter(ImageFilter.GaussianBlur(60)))
            d = ImageDraw.Draw(im); b = abs(math.sin(t * 9)) * 20
            for k, (c, kw) in enumerate([(SEM_C, {'cap': True}), (LENA_C, {'pony': True}), (HERO_C, {})]):
                person(d, 220 + k * 170, int(1200 - b + k * 15), .95, c, **kw)
            return finish(im, t, subs, shake=5)
        return title(t, 2)
    return frame

if __name__ == '__main__': run(2, LINES, sfx, frame_factory)
