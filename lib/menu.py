# menu.py
# FINAL STABLE SIMPLE MENU FOR ROUND LCD (RP2040 + CST816T)
# - Lists .py files in root directory
# - Vertical scroll with finger drag
# - Tap filename to execute
# - Uses hw.py for correct LCD / Touch pin mapping
# - Polling-based touch (no IRQ dependency)

import os, time, gc
import hw

LCD = hw.LCD
TP  = hw.TP

W, H = 240, 240

# -------- UI CONFIG --------
BG   = LCD.color(0, 0, 0)
FG   = LCD.color(230, 230, 230)
DIV  = LCD.color(50, 50, 50)
SEL  = LCD.color(0, 200, 160)

TOP = 24
ROW = 24

EXCLUDE = {
    "boot.py", "main.py", "menu.py",
    "touch.py", "hw.py"
}

# -------- HELPERS --------
def list_scripts():
    files = []
    for f in os.listdir():
        if f.endswith(".py") and f not in EXCLUDE and not f.startswith("."):
            files.append(f)
    files.sort()
    return files

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def text_center_x(s):
    return (W - len(s) * 8) // 2

def draw(items, scroll, highlight=-1):
    LCD.fill(BG)
    LCD.hline(0, TOP-1, W, DIV)

    y0 = TOP - (scroll % ROW)
    first = scroll // ROW

    for i in range(first, min(len(items), first + 12)):
        y = y0 + (i-first)*ROW
        if y > H:
            break
        if i == highlight:
            LCD.fill_rect(0, y, W, ROW, LCD.color(20, 40, 35))
            col = SEL
        else:
            col = FG

        name = items[i]
        if len(name) > 20:
            name = name[:17] + "..."
        LCD.text(name, text_center_x(name), y + 7, col)
        LCD.hline(0, y + ROW - 1, W, DIV)

    LCD.show()

# -------- MAIN --------
def main():
    items = list_scripts()
    scroll = 0
    sel = -1

    max_scroll = max(0, len(items)*ROW - (H-TOP))
    draw(items, scroll)

    last_y = None
    down_y = None
    down_t = 0

    while True:
        try:
            if TP.int.value() == 0:  # finger touching
                TP.get_point()
                x = TP.X_point
                y = TP.Y_point

                now = time.ticks_ms()

                if last_y is None:
                    last_y = y
                    down_y = y
                    down_t = now
                else:
                    dy = y - last_y
                    if abs(dy) > 3:
                        scroll -= dy
                        scroll = clamp(scroll, 0, max_scroll)
                        draw(items, scroll)
                        down_y = None
                    last_y = y

            else:
                if last_y is not None and down_y is not None:
                    if abs(down_y - last_y) < 8 and time.ticks_diff(time.ticks_ms(), down_t) < 300:
                        idx = (scroll + (last_y - TOP)) // ROW
                        if 0 <= idx < len(items):
                            draw(items, scroll, idx)
                            fn = items[idx]
                            time.sleep_ms(200)

                            LCD.fill(BG)
                            LCD.text("Running:", 60, 100, FG)
                            LCD.text(fn, text_center_x(fn), 120, SEL)
                            LCD.show()

                            gc.collect()
                            with open(fn) as f:
                                exec(f.read(), {"__name__": "__main__"})
                            gc.collect()

                            items = list_scripts()
                            max_scroll = max(0, len(items)*ROW - (H-TOP))
                            scroll = clamp(scroll, 0, max_scroll)
                            draw(items, scroll)

                last_y = None
                down_y = None

            time.sleep_ms(15)

        except Exception as e:
            LCD.fill(BG)
            LCD.text("Error:", 10, 90, SEL)
            LCD.text(str(e), 10, 110, FG)
            LCD.show()
            time.sleep(2)
            draw(items, scroll)

if __name__ == "__main__":
    main()
