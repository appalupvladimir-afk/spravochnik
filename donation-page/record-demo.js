// Запись деморежима страницы в MP4 (H.264, без звука).
// Кадры рендерятся покадрово с фиксированным временем, поэтому движение ровное
// независимо от скорости машины.
//
//   python3 -m http.server 8765          (в папке donation-page)
//   node record-demo.js [out.mp4] [--fps 60] [--scale 1]
//
// Нужны Playwright (chromium) и ffmpeg.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf(n); return i >= 0 ? Number(args[i + 1]) : d; };
const out = args.find(a => a.endsWith('.mp4')) || path.join(__dirname, 'donation-demo.mp4');
const FPS = opt('--fps', 60), SCALE = opt('--scale', 1);
const URL = process.env.PAGE_URL || 'http://127.0.0.1:8765/index.html?demo=1';
const DURATION = 19.5;

(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars'] });
  const page = await browser.newPage({ viewport: { width: 1750, height: 890 }, deviceScaleFactor: SCALE });
  page.on('pageerror', e => console.error('page error:', e.message));
  await page.goto(URL);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => window.__demo && window.__demo.on);
  await page.waitForTimeout(600);                       // текстуры персонажей загружены
  const t0 = await page.evaluate(() => { scrollTo(0, 0); return window.__demo.start; });

  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.round(DURATION * FPS);
  for (let i = 0; i < frames; i++) {
    const t = i / FPS;
    // кадр + ожидание, пока браузер полностью дорисует прокрученную страницу
    await page.evaluate(t => new Promise(done => {
      window.__demo.on = true; window.__renderAt(t);
      requestAnimationFrame(() => requestAnimationFrame(done));
    }), t0 + t);
    const png = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % FPS === 0) process.stdout.write(`\r${t.toFixed(0)} / ${DURATION} c`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => (c ? rej(new Error('ffmpeg ' + c)) : res())));
  await browser.close();
  console.log(`\nГотово: ${out}`);
})().catch(e => { console.error(e); process.exit(1); });
