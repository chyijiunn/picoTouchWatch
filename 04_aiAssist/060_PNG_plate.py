# watch_face_designB_v2.py
# Robust version: avoids blank screen if IMU/battery pin init fails.
#
# Waveshare 1.28" Round LCD (240x240) + CST816T touch (RP2040, MicroPython)
# LEFT arc  = walk progress (walknum / walkTARGET)
# RIGHT arc = run progress  (runnum / runTARGET)
import hw , time , math

LCD   = hw.LCD
Touch = hw.TP
IMU   = hw.IMU

color = LCD.color

W, H = 240, 240
CX, CY = 120, 120

BG   = color(0, 0, 0)
TEXT = color(255, 255, 255)
SUBT = color(160, 160, 160)

TRACK  = color(45, 45, 45)
WALK_C = color(0, 200, 160)
RUN_C  = color(230, 60, 60)

# Targets (use your own values or import from your main file)
walkTARGET = 100
runTARGET  = 100

walknum = 50
runnum  = 90

# Arc geometry
ARC_R = 108
ARC_THICK = 10

# Left arc (walk) and right arc (run)
WALK_START = 220
WALK_END   = 320
WALK_DIR   = 1

RUN_START  = 140
RUN_END    = 40
RUN_DIR    = -1

# Backlight
backlight = 35535
try:
    LCD.set_bl_pwm(backlight)
except Exception:
    pass

# Battery ADC (some boards wire VBAT differently; make this optional)
try:
    BAT_ADC = ADC(Pin(29))
except Exception:
    BAT_ADC = None

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def day_abbr(wday):
    return ("MON","TUE","WED","THU","FRI","SAT","SUN")[wday]

def arc_span_deg(start, end, direction):
    start %= 360
    end %= 360
    if direction == 1:
        return (end - start) % 360
    else:
        return (start - end) % 360

def iter_degrees(start, end, direction, step=1):
    start %= 360
    end %= 360
    step = abs(step) if step else 1
    if direction == 1:
        d = start
        while True:
            yield d
            if d == end:
                break
            d = (d + step) % 360
    else:
        d = start
        while True:
            yield d
            if d == end:
                break
            d = (d - step) % 360

def draw_arc_track(cx, cy, r, thick, start_deg, end_deg, direction, col):
    half = thick // 2
    for deg in iter_degrees(start_deg, end_deg, direction, step=2):
        rad = math.radians(deg)
        s = math.sin(rad)
        c = math.cos(rad)
        for rr in range(r - half, r + half + 1):
            x = int(cx + rr * s)
            y = int(cy - rr * c)
            if 0 <= x < W and 0 <= y < H:
                LCD.pixel(x, y, col)

def draw_arc_progress(cx, cy, r, thick, start_deg, end_deg, direction, reach, col):
    reach = clamp(reach, 0.0, 1.0)
    span = arc_span_deg(start_deg, end_deg, direction)
    prog = int(span * reach)
    if prog <= 0:
        return
    if direction == 1:
        prog_end = (start_deg + prog) % 360
    else:
        prog_end = (start_deg - prog) % 360
    draw_arc_track(cx, cy, r, thick, start_deg, prog_end, direction, col)

def battery_ratio():
    if BAT_ADC is None:
        return 0.68
    v = BAT_ADC.read_u16() * 3.3 / 65535 * 2
    v_full = 2.75
    v_empty = 2.25
    v = clamp(v, v_empty, v_full)
    return (v - v_empty) / (v_full - v_empty)

def draw_battery_icon(x, y, w, h, level, fg, bg):
    LCD.rect(x, y, w, h, fg)
    LCD.fill_rect(x + w, y + h // 3, 3, h // 3, fg)
    pad = 2
    fill_w = int((w - 2 * pad) * clamp(level, 0.0, 1.0))
    if fill_w > 0:
        LCD.fill_rect(x + pad, y + pad, fill_w, h - 2 * pad, fg)
    if fill_w < (w - 2 * pad):
        LCD.fill_rect(x + pad + fill_w, y + pad, (w - 2 * pad) - fill_w, h - 2 * pad, bg)

def draw_footsteps_icon(x, y, col):
    for dx, dy in ((0,0),(8,3)):
        for i in range(-2,3):
            for j in range(-3,4):
                if (i*i)/4 + (j*j)/9 <= 1:
                    LCD.pixel(x+dx+i, y+dy+j, col)

def draw_runner_icon(x, y, col):
    for i in range(-2,3):
        for j in range(-2,3):
            if i*i + j*j <= 4:
                LCD.pixel(x+i, y+j, col)
    LCD.line(x, y+3, x-3, y+12, col)
    LCD.line(x-3, y+8, x-10, y+6, col)
    LCD.line(x-3, y+10, x-9, y+14, col)
    LCD.line(x-3, y+10, x+6, y+14, col)

# IMU init (optional / robust)
try:
    IMU = touch.QMI8658()
except Exception:
    IMU = None

threhold = 300
_last_step_ms = 0

def walkandRun():
    # If no IMU, do nothing (keeps UI working)
    global walknum, runnum, _last_step_ms
    if IMU is None:
        return

    now_ms = time.ticks_ms()
    if time.ticks_diff(now_ms, _last_step_ms) < 120:
        return

    xyz1 = IMU.Read_XYZ()
    n1 = xyz1[5]
    y1 = xyz1[1]
    xyz2 = IMU.Read_XYZ()
    n2 = xyz2[5]
    y2 = xyz2[1]

    if n1 * n2 < 0:
        peak = max(abs(n1), abs(n2))
        if 10 < peak < threhold:
            walknum += 1
            _last_step_ms = now_ms
        elif peak >= threhold and min(y1, y2) < -0.8:
            runnum += 1
            _last_step_ms = now_ms

def draw_static_face():
    LCD.fill(BG)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, WALK_START, WALK_END, WALK_DIR, TRACK)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, RUN_START, RUN_END, RUN_DIR, TRACK)
    LCD.write_text("LOADING", 86, 112, 1, SUBT)
    LCD.show()

def draw_dynamic_face():
    # Clear the central areas
    LCD.fill_rect(20, 70, 200, 92, BG)
    LCD.fill_rect(12, 8, 216, 32, BG)
    LCD.fill_rect(20, 170, 200, 30, BG)

    t = time.localtime()
    hh, mm = t[3], t[4]
    mon, mday = t[1], t[2]
    wday = t[6]

    walk_reach = clamp(walknum / walkTARGET if walkTARGET else 0.0, 0.0, 1.0)
    run_reach  = clamp(runnum  / runTARGET  if runTARGET  else 0.0, 0.0, 1.0)

    # Redraw arcs (track + progress)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, WALK_START, WALK_END, WALK_DIR, TRACK)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, RUN_START, RUN_END, RUN_DIR, TRACK)
    draw_arc_progress(CX, CY, ARC_R, ARC_THICK, WALK_START, WALK_END, WALK_DIR, walk_reach, WALK_C)
    draw_arc_progress(CX, CY, ARC_R, ARC_THICK, RUN_START, RUN_END, RUN_DIR, run_reach, RUN_C)

    # Time
    time_str = "{:02d}:{:02d}".format(hh, mm)
    x_time = (W - (32 * len(time_str))) // 2
    LCD.write_text(time_str, x_time, 88, 4, TEXT)

    # Date
    date_str = "{:02d}/{:02d}  {}".format(mon, mday, day_abbr(wday))
    LCD.write_text(date_str, 62, 130, 1, SUBT)

    # Top: steps + battery
    draw_footsteps_icon(52, 66, WALK_C)
    LCD.write_text(str(walknum), 65, 40, 1, WALK_C)

    br = battery_ratio()
    draw_battery_icon(100, 12, 28, 14, br, SUBT, BG)
    LCD.write_text("{}%".format(int(br*100 + 0.5)), 210, 14, 1, SUBT)

    # Right inside: run count
    draw_runner_icon(188, 66, RUN_C)
    LCD.write_text(str(runnum), 165, 40, 1, RUN_C)

    # Bottom labels
    LCD.write_text("{}%".format(int(walk_reach*100 + 0.5)), 60, 200, 1, WALK_C)
    LCD.write_text("WALK", 50, 210, 1, SUBT)

    LCD.write_text("{}%".format(int(run_reach*100 + 0.5)), 160, 200, 1, RUN_C)
    LCD.write_text("RUN", 160, 210, 1, SUBT)

    LCD.show()

def main():
    global backlight
    draw_static_face()

    last_draw = time.ticks_ms()
    last_imu = time.ticks_ms()

    while True:
        # Brightness by gesture (same style as Waveshare demos)
        g = Touch.Gestures
        if g == 0x01:  # up
            backlight = clamp(backlight + 3000, 1, 65535)
            try: LCD.set_bl_pwm(backlight)
            except Exception: pass
            Touch.Gestures = 0
        elif g == 0x02:  # down
            backlight = clamp(backlight - 5000, 1, 65535)
            try: LCD.set_bl_pwm(backlight)
            except Exception: pass
            Touch.Gestures = 0

        now_ms = time.ticks_ms()

        if time.ticks_diff(now_ms, last_imu) >= 60:
            walkandRun()
            last_imu = now_ms

        if time.ticks_diff(now_ms, last_draw) >= 250:
            draw_dynamic_face()
            last_draw = now_ms

        time.sleep_ms(10)

if __name__ == "__main__":
    main()
