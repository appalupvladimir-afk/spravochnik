// Собирает www/ для приложения из веб-версии полки (../bookshelf/index.html):
// подключает шрифты локально, убирает всё, что нужно только сайту.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const www = join(root, "www");
rmSync(www, { recursive: true, force: true });
mkdirSync(join(www, "fonts"), { recursive: true });

const fonts = [
  ["Lora", "lora", 500], ["Lora", "lora", 700],
  ["PT Sans", "pt-sans", 400], ["PT Sans", "pt-sans", 700],
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

let html = readFileSync(join(root, "..", "bookshelf", "index.html"), "utf8");
const cut = (re, to = "") => {
  if (!re.test(html)) throw new Error("Не найдено в index.html: " + re);
  html = html.replace(re, to);
};
cut(/<link rel="preconnect"[^>]*>\n?/);
cut(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com[^>]*>/, '<link rel="stylesheet" href="fonts.css">');
cut(/<link rel="manifest"[^>]*>\n?/);
cut(/<link rel="icon"[^>]*>\n?/);
cut(/<link rel="apple-touch-icon"[^>]*>\n?/);
cut(/if\("serviceWorker" in navigator\)\{[^\n]*\n/);
// отступы от системных панелей Android
cut(/padding-top:env\(safe-area-inset-top,0px\);padding-bottom:env\(safe-area-inset-bottom,0px\);/,
  "padding-top:max(env(safe-area-inset-top,0px),var(--safe-area-inset-top,0px));" +
  "padding-bottom:max(env(safe-area-inset-bottom,0px),var(--safe-area-inset-bottom,0px));");
cut(/Книги хранятся только на этом устройстве\./, "Книги хранятся только в этом приложении на этом телефоне.");
writeFileSync(join(www, "index.html"), html);
console.log("www/ готов");
