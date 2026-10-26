import subprocess, json, os, numpy as np, wave
from scipy.signal import butter, sosfilt
SR = 44100
D = 60.0
N = int(SR * D)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(7)

# (id, start, voice, rate, pitch, text, subtitle, filter)
LINES = [
    ('n1', 0.4, 'aleksandr-hq', 85, 45, 'Я запомнил это утро по секундам. Семь сорок две.', 'Я запомнил это утро по секундам. 7:42.', None),
    ('l1', 11.0, 'anna', 115, 60, 'Что это было?!', '— Что это было?!', None),
    ('n2', 15.4, 'aleksandr-hq', 92, 45, 'Город Зет. Миллион человек. Через час здесь будет ад. Нам надо в Сосновку, к родителям. Сто сорок километров.',
     'Город Z. Миллион человек. Через час здесь будет ад. Нам надо в Сосновку, к родителям. 140 километров.', None),
    ('s1', 28.5, 'yuriy', 80, 30, 'Не учения это, сынок. Окна заклей.', '— Не учения это, сынок. Окна заклей.', None),
    ('m1', 39.6, 'tatiana', 112, 55, 'Сынок! Слушай! Не езжайте по трассе! Там', '— Сынок! Слушай! Не езжайте по трассе! Там…', 'phone'),
    ('n3', 51.9, 'aleksandr-hq', 95, 40, 'В тот момент я ещё не знал, что это был её последний звонок.', 'В тот момент я ещё не знал, что это был её последний звонок.', None),
]

def tts(i, voice, rate, pitch, text, flt):
    raw, out = f'{i}_raw.wav', f'{i}.wav'
    subprocess.run(['RHVoice-test', '-p', voice, '-r', str(rate), '-t', str(pitch), '-o', raw], input=text.encode(), check=True)
    af = 'highpass=f=350,lowpass=f=2800,volume=1.6' if flt == 'phone' else 'acompressor=threshold=-18dB:ratio=3,bass=g=3'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', af, '-ar', str(SR), '-ac', '1', out], check=True)
    with wave.open(out) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a

def t2i(t): return int(t * SR)
def env(n, a=0.01, r=0.1):
    e = np.ones(n); ai, ri = int(a * SR), int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] = np.minimum(e[-ri:], np.linspace(1, 0, ri))
    return e
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def add(buf, x, t, g=1.0):
    s = t2i(t); e = min(len(buf), s + len(x)); buf[s:e] += x[:e - s] * g

vo = np.zeros(N); sfx = np.zeros(N)
subs = []
for i, st, v, r, p, txt, sub, flt in LINES:
    a = tts(i, v, r, p, txt, flt)
    a = a / (np.abs(a).max() + 1e-9) * 0.85
    if flt == 'phone':
        a = a + bp(rng.normal(0, 0.05, len(a)), 1000, 4000)
        a[-int(0.25 * SR):] = 0  # обрыв
    add(vo, a, st)
    subs.append({'t0': st, 't1': st + len(a) / SR, 'text': sub, 'id': i})

t = np.arange(N) / SR
white = rng.normal(0, 1, N)
brown = np.cumsum(white); brown = brown - lp(brown, 20); brown /= np.abs(brown).max()

# room tone
add(sfx, brown[:t2i(57.5)] * 0.05, 0)
# clock tick 0-5
for k in range(5):
    click = bp(rng.normal(0, 1, 800), 2000, 6000) * np.exp(-np.arange(800) / 120)
    add(sfx, click, 0.2 + k, 0.35)
# rumble 5-14
n = t2i(9); r = lp(white[:n], 70); r /= np.abs(r).max()
e = np.concatenate([np.linspace(0, 1, t2i(0.6)), np.exp(-np.arange(n - t2i(0.6)) / (SR * 2.5))])
add(sfx, r * e, 5.0, 0.9)
# glass rattle 5-9
n = t2i(4); g = bp(white[:n], 2500, 7000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 28 * t[:n]))) * np.exp(-t[:n] / 1.5)
add(sfx, g, 5.1, 0.12)
# car alarms 6-35
n = t2i(29); tt = t[:n]
f = np.where((tt * 2.5) % 1 < 0.5, 900, 1250)
alarm = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5
alarm = lp(alarm, 3000) * env(n, 0.5, 3)
add(sfx, alarm * np.r_[np.full(t2i(9), 0.06), np.full(n - t2i(9), 0.025)], 6.0)
# civil defense siren 7-35
n = t2i(28); tt = t[:n]
f = 550 + 300 * np.sin(2 * np.pi * tt / 5 - np.pi / 2)
siren = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
add(sfx, siren * env(n, 3, 3), 7.0, 0.05)
# item drops 16-23
for k, tm in enumerate([16.0, 17.4, 18.8, 20.2, 21.6]):
    m = 5000; th = np.sin(2 * np.pi * 90 * np.arange(m) / SR) * np.exp(-np.arange(m) / 900)
    add(sfx, th + bp(rng.normal(0, .3, m), 300, 2000) * np.exp(-np.arange(m) / 400), tm + 0.25, 0.35)
# flicker buzz 22.6-23.6
n = t2i(1.0); buzz = np.sign(np.sin(2 * np.pi * 100 * t[:n])) * (rng.random(n) > 0.3)
add(sfx, lp(buzz, 1500) * np.repeat(rng.random(20) > 0.4, n // 20 + 1)[:n], 22.6, 0.08)
# stairwell crowd + footsteps 25-35
n = t2i(10); crowd = bp(white[:n], 250, 1100) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t[:n]) ** 2)
add(sfx, crowd * env(n, 0.5, 1), 25, 0.25)
for tm in np.sort(rng.uniform(25, 34.5, 40)):
    m = 1500; add(sfx, bp(rng.normal(0, 1, m), 150, 1500) * np.exp(-np.arange(m) / 200), tm, 0.25)
# phone vibration 35-39.4
for k in range(5):
    m = t2i(0.45); add(sfx, np.sign(np.sin(2 * np.pi * 160 * t[:m])) * env(m, .01, .05), 35.2 + k * 0.85, 0.12)
# cut click + busy tone 45.6-49
add(sfx, rng.normal(0, .5, 600), 45.55, 0.4)
for k in range(5):
    m = t2i(0.35); add(sfx, np.sin(2 * np.pi * 425 * t[:m]) * env(m, .01, .02), 46.0 + k * 0.7, 0.08)
# wind + drone 50-57.5
n = t2i(7.5); wind = bp(white[:n], 200, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t[:n]) ** 2)
drone = np.sin(2 * np.pi * (45 + 10 * t[:n] / 7.5) * t[:n]) * np.linspace(0, 1, n)
add(sfx, wind * env(n, 2, .02) * 0.2 + drone * 0.25, 50.0)
# bass hit 57.5
m = t2i(2.4); hit = np.sin(2 * np.pi * 42 * t[:m]) * np.exp(-t[:m] / 0.7) + lp(rng.normal(0, 1, m), 200) * np.exp(-t[:m] / 0.15) * 0.5
add(sfx, hit, 57.5, 0.95)

# ducking sfx under voice
venv = lp(np.abs(vo), 5); duck = 1 - 0.5 * np.clip(venv / 0.05, 0, 1)
mix = vo * 1.0 + sfx * duck
mix = np.tanh(mix * 1.1) * 0.95
mix[-t2i(0.05):] *= np.linspace(1, 0, t2i(0.05))
st = np.stack([mix, mix], 1)
with wave.open('mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
json.dump(subs, open('subs.json', 'w'), ensure_ascii=False, indent=1)
for s in subs: print(f"{s['id']}: {s['t0']:.1f}-{s['t1']:.1f}")
