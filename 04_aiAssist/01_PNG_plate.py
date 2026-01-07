# watch_face_designB.py
# Waveshare 1.28" Round LCD (240x240) + CST816T touch + QMI8658 IMU (RP2040, MicroPython)
#
# What this script does:
# - Draws a watch face similar to watch_plate.png (dark face, big time in center)
# - LEFT arc = Walk progress (walknum / walkTARGET)
# - RIGHT arc = Run progress (runnum / runTARGET)  (replaces heart-rate area)
# - Top center shows walk steps; top right shows battery %
#
# How to use:
# 1) Put touch.py into /lib on your RP2040 (you already did).
# 2) Copy this file to the root of the board (same level as main.py) and run it in Thonny.
# 3) Optionally rename this file to main.py to auto-run on boot.

from machine import Pin, ADC
import time
import math
import touch

# --------------------
# Hardware init
# --------------------
LCD = touch.LCD_1inch28()
Touch = touch.Touch_CST816T(mode=0, LCD=LCD)   # Mode 0 = gestures
IMU = touch.QMI8658()
BAT_ADC = ADC(Pin(29))  # Waveshare demo boards commonly use 29 for VBAT via divider

color = LCD.color

# --------------------
# User targets (you can reuse your values from 50_functionDesignB.py)
# --------------------
walkTARGET = 10000   # daily walk goal (steps)
runTARGET  = 1000    # daily run goal (steps)

walknum = 0
runnum  = 0

# --------------------
# UI constants
# --------------------
W, H = 240, 240
CX, CY = 120, 120

BG = color(0, 0, 0)
TEXT = color(255, 255, 255)
SUBT = color(160, 160, 160)

TRACK = color(45, 45, 45)
WALK_C = color(0, 200, 160)     # teal/green
RUN_C  = color(230, 60, 60)     # red
ACCENT = color(255, 130, 60)    # orange (optional)

# Arc geometry (angles: 0=top, 90=right, 180=bottom, 270=left; increasing = clockwise)
ARC_R = 108
ARC_THICK = 10

# Left (walk) arc: upper-left to lower-left, counter-clockwise
WALK_START = 320
WALK_END   = 220
WALK_DIR   = -1  # counter-clockwise

# Right (run) arc: upper-right to lower-right, clockwise
RUN_START  = 40
RUN_END    = 140
RUN_DIR    = 1   # clockwise

# Backlight
backlight = 35535
LCD.set_bl_pwm(backlight)

# --------------------
# Helpers
# --------------------
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def day_abbr(wday):
    # MicroPython: time.localtime()[6] => 0=Mon .. 6=Sun
    return ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")[wday]

def arc_span_deg(start, end, direction):
    """Return arc span in degrees when moving from start -> end with given direction (+1 clockwise, -1 CCW)."""
    start %= 360
    end %= 360
    if direction == 1:
        return (end - start) % 360
    else:
        return (start - end) % 360

def iter_degrees(start, end, direction, step=1):
    """Iterate degrees from start -> end inclusive, respecting direction (+1 clockwise, -1 CCW)."""
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

    # Rounded cap at the progress end
    rad = math.radians(prog_end)
    capx = int(cx + r * math.sin(rad))
    capy = int(cy - r * math.cos(rad))
    capr = max(2, thick // 2)
    for i in range(-capr, capr + 1):
        for j in range(-capr, capr + 1):
            if i * i + j * j <= capr * capr:
                x = capx + i
                y = capy + j
                if 0 <= x < W and 0 <= y < H:
                    LCD.pixel(x, y, col)

def draw_battery_icon(x, y, w, h, level, fg, bg):
    """Simple battery icon (outline + fill). level in [0..1]."""
    # outline
    LCD.rect(x, y, w, h, fg)
    # tip
    tip_w = 3
    LCD.fill_rect(x + w, y + h // 3, tip_w, h // 3, fg)
    # fill
    pad = 2
    fill_w = int((w - 2 * pad) * clamp(level, 0.0, 1.0))
    if fill_w > 0:
        LCD.fill_rect(x + pad, y + pad, fill_w, h - 2 * pad, fg)
    if fill_w < (w - 2 * pad):
        LCD.fill_rect(x + pad + fill_w, y + pad, (w - 2 * pad) - fill_w, h - 2 * pad, bg)

def draw_footsteps_icon(x, y, col):
    # Minimal "footprints" icon using two small ovals
    for dx, dy in ((0, 0), (8, 3)):
        for i in range(-2, 3):
            for j in range(-3, 4):
                if (i * i) / 4 + (j * j) / 9 <= 1:
                    LCD.pixel(x + dx + i, y + dy + j, col)

def draw_runner_icon(x, y, col):
    # Minimal "running stick figure" (very small)
    # head
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i * i + j * j <= 4:
                LCD.pixel(x + i, y + j, col)
    # body and limbs
    LCD.line(x, y + 3, x - 3, y + 12, col)      # torso
    LCD.line(x - 3, y + 8, x - 10, y + 6, col)   # arm
    LCD.line(x - 3, y + 10, x - 9, y + 14, col)  # rear leg
    LCD.line(x - 3, y + 10, x + 6, y + 14, col)  # front leg

def battery_ratio():
    # Board-specific approximation (same model as Waveshare examples)
    v = BAT_ADC.read_u16() * 3.3 / 65535 * 2
    v_full = 2.75
    v_empty = 2.25
    v = clamp(v, v_empty, v_full)
    return (v - v_empty) / (v_full - v_empty)

# --------------------
# IMU → walk/run detection (based on your walkandRun(), but more robust & cheaper)
# --------------------
threhold = 300
_last_step_ms = 0

def walkandRun():
    """Update global walknum/runnum from IMU motion.
       Replace this logic with your kettlebell classifier later, if desired.
    """
    global walknum, runnum, _last_step_ms

    now_ms = time.ticks_ms()
    if time.ticks_diff(now_ms, _last_step_ms) < 120:  # debounce
        return

    xyz1 = IMU.Read_XYZ()
    n1 = xyz1[5]              # gyro Z
    y1 = xyz1[1]              # accel Y

    xyz2 = IMU.Read_XYZ()
    n2 = xyz2[5]
    y2 = xyz2[1]

    # Zero-crossing on gyro-z suggests a swing/step cycle
    if n1 * n2 < 0:
        peak = max(abs(n1), abs(n2))
        if 10 < peak < threhold:
            walknum += 1
            _last_step_ms = now_ms
        elif peak >= threhold and min(y1, y2) < -0.8:
            runnum += 1
            _last_step_ms = now_ms

# --------------------
# Watch face drawing
# --------------------
def draw_static_face():
    LCD.fill(BG)

    # Outer arc tracks (static background)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, WALK_START, WALK_END, WALK_DIR, TRACK)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, RUN_START, RUN_END, RUN_DIR, TRACK)

    # subtle inner ring
    for rr in (86, 87):
        draw_arc_track(CX, CY, rr, 1, 0, 359, 1, color(25, 25, 25))

    LCD.show()

def draw_dynamic_face():
    # Clear dynamic areas (keep arcs region intact as much as possible)
    LCD.fill_rect(20, 70, 200, 92, BG)     # time + date area
    LCD.fill_rect(12, 8, 216, 32, BG)      # top stats area
    LCD.fill_rect(20, 170, 200, 30, BG)    # bottom stats area

    # Read time
    t = time.localtime()
    hh, mm, ss = t[3], t[4], t[5]
    mon, mday = t[1], t[2]
    wday = t[6]

    # Progress
    walk_reach = walknum / walkTARGET if walkTARGET else 0.0
    run_reach = runnum / runTARGET if runTARGET else 0.0
    walk_reach = clamp(walk_reach, 0.0, 1.0)
    run_reach = clamp(run_reach, 0.0, 1.0)

    # Re-draw tracks + progress (so old progress doesn't remain)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, WALK_START, WALK_END, WALK_DIR, TRACK)
    draw_arc_track(CX, CY, ARC_R, ARC_THICK, RUN_START, RUN_END, RUN_DIR, TRACK)
    draw_arc_progress(CX, CY, ARC_R, ARC_THICK, WALK_START, WALK_END, WALK_DIR, walk_reach, WALK_C)
    draw_arc_progress(CX, CY, ARC_R, ARC_THICK, RUN_START, RUN_END, RUN_DIR, run_reach, RUN_C)

    # Big time
    time_str = "{:02d}:{:02d}".format(hh, mm)
    # size=4 => width = 8*4*len(text) = 32*len(text)
    x_time = (W - (32 * len(time_str))) // 2
    LCD.write_text(time_str, x_time, 88, 4, TEXT)

    # Date line
    date_str = "{:02d}/{:02d}  {}".format(mon, mday, day_abbr(wday))
    LCD.write_text(date_str, 62, 130, 1, SUBT)

    # Top stats: walk steps (center top)
    draw_footsteps_icon(88, 16, WALK_C)
    LCD.write_text(str(walknum), 105, 14, 1, WALK_C)

    # Battery (top right)
    br = battery_ratio()
    draw_battery_icon(178, 12, 28, 14, br, SUBT, BG)
    LCD.write_text("{}%".format(int(br * 100 + 0.5)), 210, 14, 1, SUBT)

    # Run stats (upper-right inside face)
    draw_runner_icon(188, 66, RUN_C)
    LCD.write_text(str(runnum), 200, 60, 1, RUN_C)

    # Walk % (lower-left)
    LCD.write_text("{}%".format(int(walk_reach * 100 + 0.5)), 28, 180, 1, WALK_C)
    LCD.write_text("WALK", 26, 195, 1, SUBT)

    # Run % (lower-right)
    LCD.write_text("{}%".format(int(run_reach * 100 + 0.5)), 182, 180, 1, RUN_C)
    LCD.write_text("RUN", 186, 195, 1, SUBT)

    LCD.show()

# --------------------
# Main loop
# --------------------
def main():
    global backlight

    draw_static_face()

    last_draw = time.ticks_ms()
    last_imu = time.ticks_ms()

    while True:
        # Gesture: up/down to change brightness (as in your original file)
        g = Touch.Gestures
        if g == 0x01:  # up
            backlight = clamp(backlight + 3000, 1, 65535)
            LCD.set_bl_pwm(backlight)
            Touch.Gestures = 0
        elif g == 0x02:  # down
            backlight = clamp(backlight - 5000, 1, 65535)
            LCD.set_bl_pwm(backlight)
            Touch.Gestures = 0

        # Tilt-to-wake (optional): if face is tilted toward user, keep display awake
        # NOTE: adjust the axis/threshold if needed for your mount/orientation.
        if IMU.Read_XYZ()[0] <= -0.7:
            LCD.sleep_mode(0)
            LCD.set_bl_pwm(backlight)

        now_ms = time.ticks_ms()

        # IMU sampling
        if time.ticks_diff(now_ms, last_imu) >= 60:
            walkandRun()
            last_imu = now_ms

        # UI refresh
        if time.ticks_diff(now_ms, last_draw) >= 250:
            draw_dynamic_face()
            last_draw = now_ms

        time.sleep_ms(10)

if __name__ == "__main__":
    main()
