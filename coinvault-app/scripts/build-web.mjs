// Собирает www/ для приложения из веб-версии игры (../coinvault/index.html):
// подключает шрифты локально, чтобы игра работала без интернета.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const www = join(root, "www");
rmSync(www, { recursive: true, force: true });
mkdirSync(join(www, "fonts"), { recursive: true });

const fonts = [
  ["Ruslan Display", "ruslan-display", 400],
  ["Alegreya Sans", "alegreya-sans", 400], ["Alegreya Sans", "alegreya-sans", 500],
  ["Alegreya Sans", "alegreya-sans", 700], ["Alegreya Sans", "alegreya-sans", 800],
  ["JetBrains Mono", "jetbrains-mono", 500], ["JetBrains Mono", "jetbrains-mono", 700],
];
const ranges = {
  cyrillic: "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116",
  latin: "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD",
};
let css = "";
for (const [family, pkg, weight] of fonts) {
  for (const [subset, range] of Object.entries(ranges)) {
    const file = `${pkg}-${subset}-${weight}-normal.woff2`;
    copyFileSync(join(root, "node_modules/@fontsource", pkg, "files", file), join(www, "fonts", file));
    css += `@font-face{font-family:"${family}";font-style:normal;font-weight:${weight};font-display:swap;src:url(fonts/${file}) format("woff2");unicode-range:${range}}\n`;
  }
}
writeFileSync(join(www, "fonts.css"), css);

let html = readFileSync(join(root, "..", "coinvault", "index.html"), "utf8");
const cut = (re, to = "") => {
  if (!re.test(html)) throw new Error("Не найдено в index.html: " + re);
  html = html.replace(re, to);
};
html = html.replace(/<link rel="preconnect"[^>]*>\n?/g, "");
cut(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^>]*>/, '<link rel="stylesheet" href="fonts.css">');
// отступы от системных панелей Android
cut(/padding-top:env\(safe-area-inset-top,0px\);padding-bottom:env\(safe-area-inset-bottom,0px\)/,
  "padding-top:max(env(safe-area-inset-top,0px),var(--safe-area-inset-top,0px));" +
  "padding-bottom:max(env(safe-area-inset-bottom,0px),var(--safe-area-inset-bottom,0px))");
// без белой вспышки до загрузки стилей игры
cut(/background:#fff;color:#000/, "background:#14111b;color:#efe6d2");
writeFileSync(join(www, "index.html"), html);
console.log("www/ готов");
