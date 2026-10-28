Скрипты, которыми слои в `assets/` извлечены из скриншотов (Python 3, opencv-python-headless, numpy, scipy).
Ожидают в `<WORK>/media/` файлы `image1.png … image4.png` (это `reference/screen-1…4.png`).

    python3 cells_fit.py <WORK>                 # эллипсы эритроцитов → <WORK>/cell_ellipses.json
    python3 cells_cut.py <WORK> ../assets       # cell-A…D.png
    python3 steps_cut.py <WORK> ../assets       # step*-char.png, step*-blob.png, параметры контуров
