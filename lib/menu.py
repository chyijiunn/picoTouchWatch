# /lib/menu.py
# Robust menu for RP2040 round LCD + CST816T
# - centered filenames
# - drag scroll
# - tap to run
# - touch input: IRQ Flag + I2C polling (0x02) + INT fallback
# - uses hw.py for correct pin mapping

import os, gc
import utime as time
import hw

LCD = hw.LCD
TP  = hw.TP

W, H = 240, 240

BG   = LCD.color(0, 0, 0)
FG   = LCD.color(230, 230, 230)
DIV  = LCD.color(50, 50, 50)
SEL  = LCD.color(0, 200, 160)

TOP = 24
ROW = 24

EXCLUDE = {"boot.py", "main.py", "menu.py", "touch.py", "hw.py"}

def clamp(v, lo, hi):
    if v < lo: return lo
    if v > hi: return hi
    return v

def center_x(s):
    return (W - len(s) * 8) // 2

def list_scripts():
    items = []
    for f in os.listdir():
        if f.endswith(".py") and (f not in EXCLUDE) and (not f.startswith(".")):
            items.append(f)
    items.sort()
    return items

def draw(items, scroll_px, highlight=-1):
    LCD.fill(BG)
    LCD.hline(0, TOP - 1, W, DIV)

    y0 = TOP - (scroll_px % ROW)
    first = scroll_px // ROW

    for i in range(first, min(len(items), first + 12)):
        y = y0 + (i - first) * ROW
        if y > H:
            break

        col = FG
        if i == highlight:
            LCD.fill_rect(0, y, W, ROW, LCD.color(20, 40, 35))
            col = SEL

        name = items[i]
        if len(name) > 20:
            name = name[:17] + "..."
        LCD.text(name, center_x(name), y + 7, col)
        LCD.hline(0, y + ROW - 1, W, DIV)

    LCD.show()

def _touch_from_irq():
    try:
        if TP.Flag == 1:
            TP.Flag = 0
            return True, int(TP.X_point), int(TP.Y_point)
    except Exception:
        pass
    return False, 0, 0

def _touch_from_i2c_poll():
    # CST816T commonly uses 0x02 for touch points count
    try:
        n = TP._read_byte(0x02)
        if n and n > 0:
            TP.get_point()
            return True, int(TP.X_point), int(TP.Y_point)
    except Exception:
        pass
    return False, 0, 0

def _touch_from_int_level():
    # last-resort: if INT line is held low during touch
    try:
        if TP.int.value() == 0:
            TP.get_point()
            return True, int(TP.X_point), int(TP.Y_point)
    except Exception:
        pass
    return False, 0, 0

def read_touch():
    # priority: IRQ -> I2C poll -> INT level
    ok, x, y = _touch_from_irq()
    if ok: return True, x, y
    ok, x, y = _touch_from_i2c_poll()
    if ok: return True, x, y
    ok, x, y = _touch_from_int_level()
    if ok: return True, x, y
    return False, 0, 0

def run_script(fn):
    LCD.fill(BG)
    LCD.text("Running:", 60, 100, FG)
    show = fn if len(fn) <= 20 else (fn[:17] + "...")
    LCD.text(show, center_x(show), 120, SEL)
    LCD.show()

    gc.collect()
    g = {"__name__": "__main__", "__file__": fn}
    with open(fn, "r") as f:
        exec(f.read(), g, g)
    gc.collect()

def main():
    # ensure point mode is set (safety)
    try:
        TP.Mode = 1
        TP.Set_Mode(1)
    except Exception:
        pass

    items = list_scripts()
    scroll = 0
    max_scroll = max(0, len(items) * ROW - (H - TOP))
    draw(items, scroll)

    # Debounced press state
    pressed = False
    press_cnt = 0
    release_cnt = 0
    PRESS_TH = 2     # consecutive reads to confirm press
    RELEASE_TH = 3   # consecutive reads to confirm release

    # Gesture state
    start_y = 0
    last_y = 0
    start_ms = 0
    dragged = False

    while True:
        ok, x, y = read_touch()
        now = time.ticks_ms()

        if ok:
            release_cnt = 0
            press_cnt += 1
            if (not pressed) and press_cnt >= PRESS_TH:
                pressed = True
                start_y = y
                last_y = y
                start_ms = now
                dragged = False

            if pressed:
                dy = y - last_y
                if abs(y - start_y) >= 10:
                    dragged = True
                if abs(dy) >= 2:
                    scroll -= dy
                    scroll = clamp(scroll, 0, max_scroll)
                    draw(items, scroll)
                last_y = y

        else:
            press_cnt = 0
            release_cnt += 1
            if pressed and release_cnt >= RELEASE_TH:
                # touch released -> decide tap
                dur = time.ticks_diff(now, start_ms)
                if (not dragged) and dur <= 450:
                    idx = (scroll + (last_y - TOP)) // ROW
                    if 0 <= idx < len(items):
                        draw(items, scroll, idx)
                        time.sleep_ms(140)

                        fn = items[idx]
                        try:
                            run_script(fn)
                        except Exception as e:
                            LCD.fill(BG)
                            LCD.text("Error:", 10, 90, SEL)
                            msg = str(e)
                            LCD.text(msg[:26], 10, 110, FG)
                            LCD.show()
                            time.sleep(2)

                        # return to menu
                        items = list_scripts()
                        max_scroll = max(0, len(items) * ROW - (H - TOP))
                        scroll = clamp(scroll, 0, max_scroll)
                        draw(items, scroll)

                pressed = False

        time.sleep_ms(12)

if __name__ == "__main__":
    main()
