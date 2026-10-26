// Запись анимации в MP4 (H.264, 60 FPS, без звука).
// Кадры рендерятся детерминированно: время задаётся через window.__render(t),
// поэтому каждый кадр точный, независимо от скорости машины.
//
//   npm i playwright && npx playwright install chromium   (если ещё не установлено)
//   node record.js [выход.mp4] [--fps 60] [--scale 2]
//
// Нужен ffmpeg в PATH.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? Number(args[i + 1]) : def; };
const out = args.find(a => a.endsWith('.mp4')) || path.join(__dirname, 'blood-center-animation.mp4');
const FPS = opt('--fps', 60);
const SCALE = opt('--scale', 2);          // 1078×787 → 2156×1574 при scale 2
const W = 1078, H = 787;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?record');
  await page.waitForFunction(() => window.__ready === true);
  const duration = await page.evaluate(() => window.__duration);
  const frames = Math.round(duration * FPS) + 1;

  const ff = spawn('ffmpeg', [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-tune', 'animation',
    '-pix_fmt', 'yuv420p', '-r', String(FPS), '-movflags', '+faststart', '-an', out,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  for (let i = 0; i < frames; i++) {
    const t = Math.min(i / FPS, duration);
    await page.evaluate(t => window.__render(t), t);
    const png = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % FPS === 0) process.stdout.write(`\r${t.toFixed(1)} / ${duration} c`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => (c === 0 ? res() : rej(new Error('ffmpeg ' + c)))));
  await browser.close();
  console.log(`\nГотово: ${out} (${W * SCALE}×${H * SCALE}, ${FPS} FPS, ${frames} кадров)`);
})().catch(e => { console.error(e); process.exit(1); });
