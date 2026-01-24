# 075_runballsMazeRound_turbo_v3.py
# Waveshare 1.28" Round LCD 240x240 + QMI8658 IMU + CST816T Touch (RP2040)
# - One ball (fast)
# - Polar ring+radial maze (generated)
# - Tap to regenerate maze
# - Uses lcd_turbo partial refresh + background snapshot restore to prevent trails
#
# Put lcd_turbo.py in /lib, then run this file.

import time, math

# User's project uses touch.py / hw.py; support both.
import touch
import lcd_turbo

# ----------------------------
# Hardware init (prefer hw.py if present; fallback to touch.py)
# ----------------------------
def init_devices():
    try:
        # hw.py should expose instances LCD / IMU / TP
        from hw import LCD as _LCD, IMU as _IMU, TP as _TP
        lcd = _LCD
        imu = _IMU
        tp  = _TP
        return lcd, imu, tp
    except Exception:
        imu = touch.QMI8658()
        lcd = touch.LCD_1inch28()
        try:
            lcd.set_bl_pwm(15535)
        except Exception:
            pass
        tp = None
        try:
            tp = touch.Touch_CST816T(mode=0, LCD=lcd)
        except Exception:
            try:
                tp = touch.CST816T(mode=0, LCD=lcd)
            except Exception:
                tp = None
        return lcd, imu, tp

LCD, qmi8658, Touch = init_devices()

W, H = 240, 240
CX, CY = 120, 120
R_BOUND = 120

# ----------------------------
# Colors
# ----------------------------
c_bg   = LCD.color(0, 0, 0)
c_ring = LCD.color(40, 40, 40)
c_wall = LCD.color(80, 80, 80)
c_ball = LCD.color(255, 255, 0)

# ----------------------------
# Turbo partial updater
# ----------------------------
# max_size controls the largest dirty-rect lcd_turbo can safely send.
turbo = lcd_turbo.TurboUpdater(LCD, max_size=90)
STRIDE = turbo.stride  # usually W*2

# Access framebuffer
try:
    LCD_BUF = memoryview(LCD.buffer)  # writable memoryview
except Exception:
    LCD_BUF = None

# Background snapshot (maze only, no ball)
BG_SNAPSHOT = None
BG_MV = None

# ----------------------------
# Physics parameters (tune)
# ----------------------------
ACC_SCALE = 800.0  # bigger => faster response (was 880)
DAMP = 0.995
FRICTION = 0.010
DEAD = 0.05

BOUNCE_WALL = 0.55
BOUNCE_SEG  = 0.45
WALL_FRICTION = 0.88

# dt cap (avoid super jump but don't slow down too much)
DT_MAX = 0.12

# ----------------------------
# Maze parameters (performance-first)
# ----------------------------
MAZE_RINGS   = 4
MAZE_SECTORS = 10
MAZE_R_INNER = 24
MAZE_R_OUTER = 112
MAZE_THICK   = 6
MAZE_SEG_LEN = 18  # larger => fewer segments => faster

# ----------------------------
# Tap debounce
# ----------------------------
last_tap_ms = 0
TAP_COOLDOWN_MS = 300

# --- Random (MicroPython usually has urandom) ---
try:
    import urandom as random
except ImportError:
    import random

def _rand_int(n):
    try:
        return random.getrandbits(16) % n
    except Exception:
        return int(time.ticks_ms() % n)

# ----------------------------
# Drawing helpers
# ----------------------------
def runDot(r, x, y, color):
    x = int(x); y = int(y)
    rr = int(r)
    for i in range(-rr, rr + 1):
        for j in range(-rr, rr + 1):
            if i*i + j*j <= rr*rr:
                xi = x + i
                yj = y + j
                if 0 <= xi < W and 0 <= yj < H:
                    LCD.pixel(xi, yj, color)

def draw_circle_ring(cx, cy, r, col):
    # step=3 to reduce draw cost
    for deg in range(0, 360, 3):
        rad = math.radians(deg)
        px = int(cx + r * math.cos(rad))
        py = int(cy + r * math.sin(rad))
        if 0 <= px < W and 0 <= py < H:
            LCD.pixel(px, py, col)

def draw_thick_line(x1, y1, x2, y2, thick, col):
    dx = x2 - x1
    dy = y2 - y1
    L = math.sqrt(dx*dx + dy*dy)
    if L == 0:
        return
    nx = -dy / L
    ny =  dx / L
    half = int(thick) // 2
    for k in range(-half, half + 1):
        ox = int(nx * k)
        oy = int(ny * k)
        LCD.line(int(x1 + ox), int(y1 + oy), int(x2 + ox), int(y2 + oy), col)

# ----------------------------
# Polar maze generation -> WALLS
# Store wall as ints to save RAM:
#   (x1,y1,x2,y2,th,minx,maxx,miny,maxy)
# ----------------------------
def polar_to_xy(r, a):
    return (CX + r * math.cos(a), CY + r * math.sin(a))

def _add_wall(walls, x1, y1, x2, y2, thick):
    # convert to ints early (RAM + speed)
    x1 = int(x1); y1 = int(y1); x2 = int(x2); y2 = int(y2)
    thick = int(thick)
    minx = x1 if x1 < x2 else x2
    maxx = x2 if x2 > x1 else x1
    miny = y1 if y1 < y2 else y2
    maxy = y2 if y2 > y1 else y1
    walls.append((x1, y1, x2, y2, thick, minx, maxx, miny, maxy))

def add_arc_segments(walls, r, a0, a1, thick, seg_len=18):
    da = a1 - a0
    if da < 0:
        da += 2 * math.pi
    arc_len = abs(r * da)
    n = max(2, int(arc_len / seg_len))
    for k in range(n):
        aa0 = a0 + da * (k / n)
        aa1 = a0 + da * ((k + 1) / n)
        x0, y0 = polar_to_xy(r, aa0)
        x1, y1 = polar_to_xy(r, aa1)
        _add_wall(walls, x0, y0, x1, y1, thick)

def add_radial_segment(walls, a, r0, r1, thick):
    x0, y0 = polar_to_xy(r0, a)
    x1, y1 = polar_to_xy(r1, a)
    _add_wall(walls, x0, y0, x1, y1, thick)

def generate_polar_maze(rings, sectors, r_inner, r_outer, thick, seg_len):
    r_edges = [r_inner + (r_outer - r_inner) * i / rings for i in range(rings + 1)]
    dtheta = 2 * math.pi / sectors

    out_wall = [[True for _ in range(sectors)] for _ in range(rings - 1)]
    cw_wall  = [[True for _ in range(sectors)] for _ in range(rings)]
    visited  = [[False for _ in range(sectors)] for _ in range(rings)]

    stack = [(0, _rand_int(sectors))]
    visited[stack[0][0]][stack[0][1]] = True

    def neighbors(r, s):
        nb = []
        nb.append((r, (s + 1) % sectors, "cw"))
        nb.append((r, (s - 1) % sectors, "ccw"))
        if r < rings - 1: nb.append((r + 1, s, "out"))
        if r > 0:         nb.append((r - 1, s, "in"))
        return nb

    while stack:
        r, s = stack[-1]
        cand = []
        for nr, ns, d in neighbors(r, s):
            if not visited[nr][ns]:
                cand.append((nr, ns, d))
        if not cand:
            stack.pop()
            continue

        nr, ns, d = cand[_rand_int(len(cand))]

        if d == "out":
            out_wall[r][s] = False
        elif d == "in":
            out_wall[r - 1][s] = False
        elif d == "cw":
            cw_wall[r][s] = False
        elif d == "ccw":
            cw_wall[r][(s - 1) % sectors] = False

        visited[nr][ns] = True
        stack.append((nr, ns))

    walls = []
    # center island ring
    add_arc_segments(walls, r_edges[0], 0, 2*math.pi, thick, seg_len=seg_len)

    # arc walls between rings
    for r in range(rings - 1):
        rr = r_edges[r + 1]
        for s in range(sectors):
            if out_wall[r][s]:
                a0 = s * dtheta
                a1 = (s + 1) * dtheta
                add_arc_segments(walls, rr, a0, a1, thick, seg_len=seg_len)

    # radial walls
    for r in range(rings):
        r0 = r_edges[r]
        r1 = r_edges[r + 1]
        for s in range(sectors):
            if cw_wall[r][s]:
                a = (s + 1) * dtheta
                add_radial_segment(walls, a, r0, r1, thick)

    return walls

# ----------------------------
# Collision
# ----------------------------
def collide_with_outer_circle(b):
    dx = b["x"] - CX
    dy = b["y"] - CY
    dist = math.sqrt(dx*dx + dy*dy)
    max_r = R_BOUND - b["r"]
    if dist > max_r and dist > 0:
        nx = dx / dist
        ny = dy / dist
        b["x"] = CX + nx * max_r
        b["y"] = CY + ny * max_r
        vn = b["vx"]*nx + b["vy"]*ny
        b["vx"] = b["vx"] - (1.0 + BOUNCE_WALL) * vn * nx
        b["vy"] = b["vy"] - (1.0 + BOUNCE_WALL) * vn * ny
        b["vx"] *= 0.92
        b["vy"] *= 0.92

def collide_ball_with_wall(b, wall):
    x1, y1, x2, y2, thick, minx, maxx, miny, maxy = wall
    px = b["x"]; py = b["y"]
    rad = b["r"] + (thick * 0.5)

    # AABB reject (fast)
    if px < (minx - rad) or px > (maxx + rad) or py < (miny - rad) or py > (maxy + rad):
        return

    vx = x2 - x1; vy = y2 - y1
    wx = px - x1; wy = py - y1
    vv = vx*vx + vy*vy
    if vv == 0:
        return

    t = (wx*vx + wy*vy) / vv
    if t < 0.0: t = 0.0
    elif t > 1.0: t = 1.0

    cxp = x1 + t * vx
    cyp = y1 + t * vy

    dx = px - cxp
    dy = py - cyp
    d2 = dx*dx + dy*dy
    if d2 >= rad*rad:
        return

    dist = math.sqrt(d2) if d2 > 0 else 0.0001
    nx = dx / dist
    ny = dy / dist

    overlap = rad - dist
    b["x"] += nx * overlap
    b["y"] += ny * overlap

    vn = b["vx"]*nx + b["vy"]*ny
    if vn < 0:
        b["vx"] = b["vx"] - (1.0 + BOUNCE_SEG) * vn * nx
        b["vy"] = b["vy"] - (1.0 + BOUNCE_SEG) * vn * ny
        b["vx"] *= WALL_FRICTION
        b["vy"] *= WALL_FRICTION

# ----------------------------
# Tap detect (robust)
# ----------------------------
def is_tap():
    global last_tap_ms
    if Touch is None:
        return False

    now = time.ticks_ms()
    if time.ticks_diff(now, last_tap_ms) <= TAP_COOLDOWN_MS:
        return False

    # Method 1: Flag
    try:
        if getattr(Touch, "Flag", 0) == 1:
            try:
                Touch.Flag = 0
            except Exception:
                pass
            last_tap_ms = now
            return True
    except Exception:
        pass

    # Method 2: Gestures
    try:
        g = getattr(Touch, "Gestures", 0)
        if g:
            try:
                Touch.Gestures = 0
            except Exception:
                pass
            last_tap_ms = now
            return True
    except Exception:
        pass

    # Method 3: get_point / Get_Point
    for fn_name in ("get_point", "Get_Point"):
        try:
            fn = getattr(Touch, fn_name, None)
            if fn:
                p = fn()
                if p:
                    last_tap_ms = now
                    return True
        except Exception:
            pass

    return False

# ----------------------------
# Background snapshot & restore
# ----------------------------
def snapshot_background():
    global BG_SNAPSHOT, BG_MV
    if LCD_BUF is None:
        BG_SNAPSHOT = None
        BG_MV = None
        return
    try:
        BG_SNAPSHOT = bytearray(LCD_BUF)  # full screen copy
        BG_MV = memoryview(BG_SNAPSHOT)
    except Exception:
        BG_SNAPSHOT = None
        BG_MV = None

def restore_rect(min_x, min_y, w, h):
    if BG_MV is None or LCD_BUF is None:
        return False
    row_bytes = w * 2
    base = min_x * 2
    for rr in range(h):
        start = (min_y + rr) * STRIDE + base
        LCD_BUF[start:start + row_bytes] = BG_MV[start:start + row_bytes]
    return True

def restore_full():
    if BG_MV is None or LCD_BUF is None:
        return False
    try:
        LCD_BUF[:] = BG_MV
        return True
    except Exception:
        return False

def compute_dirty_rect(x, y, r, padding=6):
    lx = turbo.last_x
    ly = turbo.last_y
    if lx is None or ly is None:
        return (0, 0, W, H, True)

    x = int(x); y = int(y)
    lx = int(lx); ly = int(ly)
    r = int(r)

    min_x = min(x, lx) - r - padding
    max_x = max(x, lx) + r + padding
    min_y = min(y, ly) - r - padding
    max_y = max(y, ly) + r + padding

    if min_x < 0: min_x = 0
    if min_y < 0: min_y = 0
    if max_x > W: max_x = W
    if max_y > H: max_y = H

    ww = int(max_x - min_x)
    hh = int(max_y - min_y)

    if ww <= 0 or hh <= 0:
        return (0, 0, 0, 0, False)

    # Must fit turbo scratch
    if ww > turbo.max_size or hh > turbo.max_size:
        return (0, 0, W, H, True)

    return (min_x, min_y, ww, hh, False)

# ----------------------------
# Ball + Maze state
# ----------------------------
WALLS = []
ball = {"x": float(CX), "y": float(CY), "vx": 0.0, "vy": 0.0, "r": 4, "c": c_ball}

def spawn_ball():
    dr = (MAZE_R_OUTER - MAZE_R_INNER) / MAZE_RINGS
    r_spawn = MAZE_R_INNER + dr * 0.55
    a = (_rand_int(MAZE_SECTORS) + 0.5) * (2 * math.pi / MAZE_SECTORS)
    x, y = polar_to_xy(r_spawn, a)
    ball["x"], ball["y"] = x, y
    ball["vx"], ball["vy"] = 0.0, 0.0

def draw_maze_to_buffer():
    LCD.fill_rect(0, 0, W, H, c_bg)
    draw_circle_ring(CX, CY, R_BOUND - 1, c_ring)
    for wall in WALLS:
        draw_thick_line(wall[0], wall[1], wall[2], wall[3], wall[4], c_wall)

def regen_maze():
    global WALLS
    WALLS = generate_polar_maze(
        rings=MAZE_RINGS,
        sectors=MAZE_SECTORS,
        r_inner=MAZE_R_INNER,
        r_outer=MAZE_R_OUTER,
        thick=MAZE_THICK,
        seg_len=MAZE_SEG_LEN
    )

    # Draw background (maze only) to buffer, snapshot it, then draw ball, then show once.
    draw_maze_to_buffer()
    snapshot_background()
    spawn_ball()
    runDot(ball["r"], ball["x"], ball["y"], ball["c"])
    LCD.show()

    # Initialize turbo history so the next refresh is partial
    turbo.last_x = int(ball["x"])
    turbo.last_y = int(ball["y"])

# First draw
regen_maze()

# ----------------------------
# Main loop
# ----------------------------
last_ms = time.ticks_ms()

while True:
    if is_tap():
        regen_maze()

    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000.0
    last_ms = now_ms
    if dt <= 0:
        dt = 0.01
    if dt > DT_MAX:
        dt = DT_MAX

    # Read IMU once
    xg, yg, zg, gx, gy, gz = qmi8658.Read_XYZ()

    # Normalize (reduce dynamic accel effect)
    gmag = math.sqrt(xg*xg + yg*yg + zg*zg)
    if gmag > 0:
        xg /= gmag
        yg /= gmag

    # Deadzone
    if abs(xg) < DEAD: xg = 0.0
    if abs(yg) < DEAD: yg = 0.0

    # Tilt -> plane acceleration
    ax =  yg * ACC_SCALE
    ay = -xg * ACC_SCALE

    # --- Physics integrate ---
    ball["vx"] += ax * dt
    ball["vy"] += ay * dt

    ball["vx"] *= DAMP
    ball["vy"] *= DAMP

    spd = math.sqrt(ball["vx"]*ball["vx"] + ball["vy"]*ball["vy"])
    if spd < 30:
        ball["vx"] *= (1.0 - FRICTION)
        ball["vy"] *= (1.0 - FRICTION)

    ball["x"] += ball["vx"] * dt
    ball["y"] += ball["vy"] * dt

    # --- Collisions ---
    collide_with_outer_circle(ball)
    for wall in WALLS:
        collide_ball_with_wall(ball, wall)
    collide_with_outer_circle(ball)

    # --- Render: restore background in dirty rect -> draw ball -> partial refresh ---
    min_x, min_y, ww, hh, need_full = compute_dirty_rect(ball["x"], ball["y"], ball["r"], padding=6)

    if need_full:
        # Full restore (or redraw if snapshot unavailable)
        if not restore_full():
            draw_maze_to_buffer()
        runDot(ball["r"], ball["x"], ball["y"], ball["c"])
        LCD.show()
        turbo.last_x = int(ball["x"])
        turbo.last_y = int(ball["y"])
    else:
        # Restore dirty rect from snapshot
        ok = restore_rect(min_x, min_y, ww, hh)
        if not ok:
            # fallback redraw (rare)
            draw_maze_to_buffer()
        runDot(ball["r"], ball["x"], ball["y"], ball["c"])
        turbo.refresh(ball["x"], ball["y"], ball["r"], padding=6)

    time.sleep_ms(10)
