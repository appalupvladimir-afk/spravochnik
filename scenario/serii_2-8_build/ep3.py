"""Серия 3 «Подвал»."""
from common import *

LINES = [
    (1.4, 'SEM', 'Не трогай!|Это не снег.', '— Не трогай! Это не снег.', 'shout'),
    (9.4, 'GLEB', 'Что несёте?|Еда, лекарства — всё в общий котёл.|Такие правила.', '— Что несёте? Еда, лекарства — всё в общий котёл. Такие правила.', None),
    (17.0, 'N', 'Пришлось отдать половину еды…|за право не умереть на улице.', 'Пришлось отдать половину еды… за право не умереть на улице.', None),
    (31.0, 'LENA', 'Ты слышишь?|Опять.|Там ребёнок…', '— Ты слышишь? Опять. Там ребёнок…', None),
    (37.5, 'HERO', 'Спи.|Утром разберёмся.', '— Спи. Утром разберёмся.', None),
    (46.0, 'N', 'Утром…|Лена исчезла.', 'Утром… Лена исчезла.', None),
]

def sfx():
    ev = [(0, wind(6), .25), (6.3, knock(), .6), (6.7, knock(), .6), (7.1, knock(), .6), (8.0, creak(2.5), .35), (8.6, clang(2.5), .35),
          (10, room(20), .08), (12, crowd(18), .12), (24, heartbeat(3, 90), .15), (30, room(15), .06), (31.5, child_cry(12), .025),
          (45, room(12.5), .05), (TITLE_T, bass_hit(), .95)]
    for k in np.arange(47.5, 57.3, 1.3): ev.append((float(k), drip(), .25))
    return ev

def frame_factory(subs):
    rs = np.random.default_rng
    street = canvas((95, 95, 92), (60, 60, 60)); d = ImageDraw.Draw(street)
    city(d, SW, 1000, rs(21), (45, 46, 46), .0, 1.2); d.rectangle([0, 1000, SW, SH], fill=(70, 70, 68))
    wall = canvas((55, 55, 50), (40, 40, 37)); d = ImageDraw.Draw(wall)
    for y in range(0, SH, 90): d.line([0, y, SW, y], fill=(48, 48, 44), width=3)
    bunker = canvas((38, 36, 30), (22, 21, 18)); d = ImageDraw.Draw(bunker)
    d.rectangle([0, 900, SW, SH], fill=(30, 29, 26))
    for k in range(3):  # нары
        x = 60 + k * 260; d.rectangle([x, 700, x + 220, 720], fill=(60, 55, 45)); d.rectangle([x, 880, x + 220, 900], fill=(60, 55, 45))
        d.rectangle([x, 560, x + 10, 1000], fill=(50, 46, 40)); d.rectangle([x + 210, 560, x + 220, 1000], fill=(50, 46, 40))
    rs4 = rs(14)
    for k in range(9): person(d, rs4.uniform(40, SW - 40), rs4.uniform(1050, 1250), rs4.uniform(.45, .7), (14, 13, 12))

    def lamps(im, t, dim=1.0):
        d = ImageDraw.Draw(im)
        for x in (180, 600):
            d.line([x, 0, x, 120], fill=(20, 20, 20), width=3); fl = .85 + .15 * math.sin(t * 23 + x)
            glow(im, x, 140, 110, (255, 210, 120), int(140 * dim * fl)); d.ellipse([x - 14, 126, x + 14, 154], fill=(255, 230, 160))

    def frame(t):
        if t < 6:
            im = street.copy().convert('RGBA'); particles(im, t, 180, (190, 190, 185), 60, 3, 1, drift=15)
            d = ImageDraw.Draw(im); person(d, 330, 1500, 2.2, LENA_C, pony=True)
            d.line([450, 1000, 640, 900], fill=LENA_C, width=46)
            if t > 1.3: d.line([780, 760, 650, 880], fill=SEM_C, width=40)
            return finish(im, t, subs, shake=1)
        if t < 14:
            im = wall.copy().convert('RGBA'); d = ImageDraw.Draw(im); p = ease((t - 8.4) / 2)
            d.rectangle([110, 300, 690, 1180], fill=(10, 10, 10))
            if p > 0:
                person(d, 400, 1180, 1.6, GLEB_C, bulky=True, light=(255, 240, 200)); cone(im, 520, 860, 120, 18, 700, 90)
                for k in range(5): person(d, 200 + k * 90, 1140, .9, (8, 8, 8))
            dw = int(580 * (1 - p)); d.rectangle([110, 300, 110 + dw, 1180], fill=(70, 62, 50))
            for y in (420, 740, 1060): d.rectangle([110 + dw - 70, y, 110 + dw - 30, y + 60], fill=(50, 44, 35))
            d.text((110 + dw // 2, 600), '☢', font=font(120), fill=(140, 120, 40), anchor='mm')
            return finish(im, t, subs, shake=2 if 6.3 < t < 7.4 else .8)
        if t < 24:
            im = bunker.copy().convert('RGBA'); lamps(im, t); d = ImageDraw.Draw(im)
            person(d, 480, 1230, 1.0, GLEB_C, bulky=True); person(d, 260, 1220, .95, (18, 20, 16), gun=True)
            for k in range(min(5, int((t - 14) * 1.2))): d.rounded_rectangle([560 + k * 40, 1000 - k * 8, 595 + k * 40, 1050 - k * 8], 6, fill=(150, 150, 140))
            person(d, 140, 1300, .9, HERO_C); person(d, 680, 1300, .85, LENA_C, pony=True)
            return finish(zoom(im, 1 + (t - 14) * .01), t, subs, warm=True)
        if t < 30:
            im = canvas((24, 28, 40), (16, 18, 26)); d = ImageDraw.Draw(im)
            d.polygon([(0, 0), (SW, 0), (SW, SH), (0, SH)], fill=SEM_C); d.rectangle([150, 500, 650, 1100], fill=(14, 16, 24))  # карман
            y = lerp(300, 650, ease((t - 24.5) / 2.5))
            d.rectangle([250, y, 550, y + 320], fill=(225, 225, 215)); d.text((400, y + 110), 'КАЛИЯ', font=font(44), fill=(30, 30, 120), anchor='mm')
            d.text((400, y + 170), 'ЙОДИД', font=font(44), fill=(30, 30, 120), anchor='mm'); d.rectangle([150, 950, 650, 1100], fill=(14, 16, 24))
            return finish(im, t, subs, warm=True)
        if t < 45:
            im = bunker.copy().convert('RGBA'); lamps(im, t, .25); d = ImageDraw.Draw(im)
            person(d, 290, 1500, 1.9, HERO_C); person(d, 520, 1520, 1.8, LENA_C, pony=True)
            cone(im, 760, 600, 200, 4, 300, 25, (180, 180, 200))
            return finish(zoom(im, 1 + (t - 30) * .008, .6, .6), t, subs, dark=.45, warm=True)
        if t < 53:
            im = bunker.copy().convert('RGBA'); lamps(im, t, .9); d = ImageDraw.Draw(im)
            d.rectangle([380, 1150, 760, 1250], fill=(60, 50, 40)); d.rectangle([0, 1150, 340, 1250], fill=(50, 54, 40))
            person(d, 160, 1450, 1.4, HERO_C)
            return finish(zoom(im, 1 + (t - 45) * .025, .7, .85), t, subs, warm=True)
        if t < TITLE_T:
            im = wall.copy().convert('RGBA'); d = ImageDraw.Draw(im)
            d.rectangle([200, 300, 600, 1150], fill=(4, 4, 4)); a = ease((t - 53) / 4) * 25 + 15
            d.polygon([(200, 300), (200 + 400 * (1 - a / 90), 330), (200 + 400 * (1 - a / 90), 1120), (200, 1150)], fill=(80, 55, 40))
            y = 900 + ((t * 300) % 300); d.ellipse([480, y, 490, y + 14], fill=(150, 160, 170))
            return finish(zoom(im, 1 + (t - 53) * .03), t, subs)
        return title(t, 3)
    return frame

if __name__ == '__main__': run(3, LINES, sfx, frame_factory)
