# polar_maze_oneball_fast.py
# Waveshare 1.28" Round LCD (240x240) + CST816T touch + QMI8658 IMU
# Features:
#   - One-ball "tilt labyrinth" physics (fast)
#   - Polar (ring + radial) maze generation (perfect maze)
#   - Tap screen to regenerate a new maze
#   - Static background drawn once per maze; per-frame restores background buffer if available

import time, math, touch

# --- Random (MicroPython usually has urandom) ---
try:
    import urandom as random
except ImportError:
    import random

# ----------------------------
# Hardware init
# ----------------------------
qmi8658 = touch.QMI8658()
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

# Touch init (robust across minor driver naming differences)
Touch = None
try:
    Touch = touch.Touch_CST816T(mode=0, LCD=LCD)
except Exception:
    try:
        Touch = touch.CST816T(mode=0, LCD=LCD)
    except Exception:
        Touch = None

W, H = 240, 240
CX, CY = 120, 120
R_BOUND = 120

# Colors
c_bg   = LCD.color(0, 0, 0)
c_ring = LCD.color(40, 40, 40)
c_wall = LCD.color(80, 80, 80)
c_ball = LCD.color(255, 255, 0)

# ----------------------------
# Physics parameters (tune)
# ----------------------------
ACC_SCALE = 880.0   # tilt -> px/s^2
DAMP = 0.995        # air damping (closer to 1 = more slippery)
FRICTION = 0.010    # low-speed friction
DEAD = 0.05         # deadzone (small tilt won't move)

BOUNCE_WALL = 0.55
BOUNCE_SEG  = 0.45
WALL_FRICTION = 0.88

# ----------------------------
# Maze parameters (tune for performance)
# ----------------------------
MAZE_RINGS   = 5
MAZE_SECTORS = 12
MAZE_R_INNER = 22
MAZE_R_OUTER = 112
MAZE_THICK   = 8
MAZE_SEG_LEN = 14  # bigger => fewer segments => faster

# Tap debounce
last_tap_ms = 0
TAP_COOLDOWN_MS = 350

# ----------------------------
# Helpers
# ----------------------------
def _rand_int(n):
    try:
        return random.getrandbits(16) % n
    except Exception:
        return int(time.ticks_ms() % n)

def _get_lcd_writable_buffer(lcd):
    """
    Try to get the internal framebuffer buffer so we can snapshot/restore
    the static background quickly. If not available, we fall back to full redraw.
    """
    def _ok(b):
        # writable bytearray or writable memoryview
        if isinstance(b, bytearray):
            return True
        if isinstance(b, memoryview) and not getattr(b, "readonly", True):
            return True
        return False

    for name in ("buffer", "buf", "_buffer", "_buf"):
        b = getattr(lcd, name, None)
        if _ok(b):
            return b

    for fb_name in ("framebuf", "fb", "_framebuf"):
        fb = getattr(lcd, fb_name, None)
        if fb is not None:
            b = getattr(fb, "buf", None)
            if _ok(b):
                return b

    return None

LCD_BUF = _get_lcd_writable_buffer(LCD)
BG_SNAPSHOT = None

def runDot(r, x, y, color):
    x = int(x); y = int(y)
    for i in range(-r, r + 1):
        for j in range(-r, r + 1):
            if i*i + j*j <= r*r:
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

def polar_to_xy(r, a):
    return (CX + r * math.cos(a), CY + r * math.sin(a))

def _add_wall(walls, x1, y1, x2, y2, thick):
    # Precompute AABB for faster collision culling
    minx = x1 if x1 < x2 else x2
    maxx = x2 if x2 > x1 else x1
    miny = y1 if y1 < y2 else y2
    maxy = y2 if y2 > y1 else y1
    walls.append((x1, y1, x2, y2, thick, minx, maxx, miny, maxy))

def add_arc_segments(walls, r, a0, a1, thick, seg_len=14):
    da = a1 - a0
    if da < 0:
        da += 2 * math.pi
    arc_len = abs(r * da)
    n = max(3, int(arc_len / seg_len))
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
    # rings rings => rings+1 radius boundaries
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

    # Center island (full ring)
    add_arc_segments(walls, r_edges[0], 0, 2*math.pi, thick, seg_len=seg_len)

    # Arc walls between rings
    for r in range(rings - 1):
        rr = r_edges[r + 1]
        for s in range(sectors):
            if out_wall[r][s]:
                a0 = s * dtheta
                a1 = (s + 1) * dtheta
                add_arc_segments(walls, rr, a0, a1, thick, seg_len=seg_len)

    # Radial walls
    for r in range(rings):
        r0 = r_edges[r]
        r1 = r_edges[r + 1]
        for s in range(sectors):
            if cw_wall[r][s]:
                a = (s + 1) * dtheta
                add_radial_segment(walls, a, r0, r1, thick)

    return walls

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

def collide_ball_with_segment(b, wall):
    # wall: (x1,y1,x2,y2,th,minx,maxx,miny,maxy)
    x1, y1, x2, y2, thick, minx, maxx, miny, maxy = wall
    px = b["x"]; py = b["y"]

    rad = b["r"] + (thick * 0.5)

    # AABB early reject
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

def _is_tap():
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
# Static background build + snapshot
# ----------------------------
WALLS = []

def build_static_background():
    global BG_SNAPSHOT
    LCD.fill_rect(0, 0, W, H, c_bg)
    draw_circle_ring(CX, CY, R_BOUND - 1, c_ring)
    for wall in WALLS:
        x1, y1, x2, y2, th = wall[0], wall[1], wall[2], wall[3], wall[4]
        draw_thick_line(x1, y1, x2, y2, th, c_wall)
    LCD.show()

    # Snapshot the internal buffer for fast restore each frame
    if LCD_BUF is not None:
        try:
            BG_SNAPSHOT = bytearray(LCD_BUF)
        except Exception:
            BG_SNAPSHOT = None
    else:
        BG_SNAPSHOT = None

def restore_background_fast():
    if BG_SNAPSHOT is None or LCD_BUF is None:
        return False
    try:
        LCD_BUF[:] = BG_SNAPSHOT
        return True
    except Exception:
        return False

# ----------------------------
# Ball state (one ball)
# ----------------------------
ball = {"x": float(CX), "y": float(CY), "vx": 0.0, "vy": 0.0, "r": 4, "c": c_ball}

def spawn_ball():
    dr = (MAZE_R_OUTER - MAZE_R_INNER) / MAZE_RINGS
    r_spawn = MAZE_R_INNER + dr * 0.55
    a = (_rand_int(MAZE_SECTORS) + 0.5) * (2 * math.pi / MAZE_SECTORS)
    x, y = polar_to_xy(r_spawn, a)
    ball["x"] = x
    ball["y"] = y
    ball["vx"] = 0.0
    ball["vy"] = 0.0

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
    spawn_ball()
    build_static_background()

# First maze
regen_maze()

# ----------------------------
# Main loop
# ----------------------------
last_ms = time.ticks_ms()

while True:
    if _is_tap():
        regen_maze()

    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000.0
    last_ms = now_ms
    if dt <= 0:
        dt = 0.01
    if dt > 0.05:
        dt = 0.05

    # Read IMU once
    xg, yg, zg, gx, gy, gz = qmi8658.Read_XYZ()

    # Normalize to reduce dynamic accel impact
    gmag = math.sqrt(xg*xg + yg*yg + zg*zg)
    if gmag > 0:
        xg /= gmag
        yg /= gmag

    # Deadzone
    if abs(xg) < DEAD: xg = 0.0
    if abs(yg) < DEAD: yg = 0.0

    # Tilt -> plane acceleration
    # If direction feels inverted, flip signs here:
    ax =  yg * ACC_SCALE
    ay = -xg * ACC_SCALE

    # Restore background (fast) or fallback full redraw
    if not restore_background_fast():
        # Fallback: slower but always correct
        LCD.fill_rect(0, 0, W, H, c_bg)
        draw_circle_ring(CX, CY, R_BOUND - 1, c_ring)
        for wall in WALLS:
            x1, y1, x2, y2, th = wall[0], wall[1], wall[2], wall[3], wall[4]
            draw_thick_line(x1, y1, x2, y2, th, c_wall)

    # Physics integrate
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

    # Collisions
    collide_with_outer_circle(ball)
    for wall in WALLS:
        collide_ball_with_segment(ball, wall)
    collide_with_outer_circle(ball)

    # Draw ball
    runDot(ball["r"], ball["x"], ball["y"], ball["c"])

    LCD.show()
    time.sleep_ms(10)
