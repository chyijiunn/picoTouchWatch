import time, math , touch
from hw import LCD, IMU ,TP

# ---- 亂數（MicroPython 常用 urandom）----
try:
    import urandom as random
except ImportError:
    import random

Touch = TP

# 觸控（你要點一下重生迷宮就需要它）

W, H = 240, 240
CX, CY = 120, 120
R_BOUND = 120

# 顏色
c_bg   = LCD.color(0, 0, 0)
c_ring = LCD.color(40, 40, 40)
c_wall = LCD.color(80, 80, 80)
c1 = LCD.color(255, 255, 0)
c2 = LCD.color(0, 220, 160)
c3 = LCD.color(255, 80, 80)

# ----------------------------
# 物理參數（保留你的）
# ----------------------------
ACC_SCALE = 880.0
DAMP = 0.995
FRICTION = 0.010
DEAD = 0.05

BOUNCE_WALL = 0.55
BOUNCE_SEG  = 0.45
WALL_FRICTION = 0.88

# ----------------------------
# 迷宮參數（你可調難度/效能）
# ----------------------------
MAZE_RINGS = 4
MAZE_SECTORS = 12
MAZE_R_INNER = 20
MAZE_R_OUTER = 112
MAZE_THICK = 5
MAZE_SEG_LEN = 14   # 圓弧離散成線段的長度：越小越精細、越吃效能

# ----------------------------
# 小工具
# ----------------------------
def rand_int(n):
    # 0..n-1
    try:
        return random.getrandbits(16) % n
    except Exception:
        return int(time.ticks_ms() % n)

def runDot(r, x, y, color):
    x = int(x); y = int(y)
    for i in range(-r, r+1):
        for j in range(-r, r+1):
            if i*i + j*j <= r*r:
                xi = x + i
                yj = y + j
                if 0 <= xi < W and 0 <= yj < H:
                    LCD.pixel(xi, yj, color)

def draw_circle_ring(cx, cy, r, col):
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
    for k in range(-half, half+1):
        ox = int(nx * k)
        oy = int(ny * k)
        LCD.line(int(x1+ox), int(y1+oy), int(x2+ox), int(y2+oy), col)

# ----------------------------
# 極座標迷宮：圓弧牆/放射牆 -> 線段牆 WALLS
# ----------------------------
def polar_to_xy(r, a):
    return (CX + r * math.cos(a), CY + r * math.sin(a))

def add_arc_segments(walls, r, a0, a1, thick, seg_len=7):
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
        walls.append((x0, y0, x1, y1, thick))

def add_radial_segment(walls, a, r0, r1, thick):
    x0, y0 = polar_to_xy(r0, a)
    x1, y1 = polar_to_xy(r1, a)
    walls.append((x0, y0, x1, y1, thick))

def generate_polar_maze(rings, sectors, r_inner, r_outer, thick, seg_len):
    # rings 個環 => rings+1 個半徑邊界
    r_edges = [r_inner + (r_outer - r_inner) * i / rings for i in range(rings + 1)]
    dtheta = 2 * math.pi / sectors

    # out_wall[r][s]：半徑 r_edges[r+1] 的弧牆是否存在（r 0..rings-2）
    out_wall = [[True for _ in range(sectors)] for _ in range(rings - 1)]
    # cw_wall[r][s]：角度 (s+1)*dtheta 的放射牆是否存在（r 0..rings-1）
    cw_wall  = [[True for _ in range(sectors)] for _ in range(rings)]
    visited = [[False for _ in range(sectors)] for _ in range(rings)]

    # DFS stack（避免遞迴）
    stack = [(0, rand_int(sectors))]
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

        nr, ns, d = cand[rand_int(len(cand))]

        # 打通牆
        if d == "out":
            if r < rings - 1:
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

    # 中心島：完整圓弧牆
    add_arc_segments(walls, r_edges[0], 0, 2*math.pi, thick, seg_len=seg_len)

    # ring 間弧牆
    for r in range(rings - 1):
        rr = r_edges[r + 1]
        for s in range(sectors):
            if out_wall[r][s]:
                a0 = s * dtheta
                a1 = (s + 1) * dtheta
                add_arc_segments(walls, rr, a0, a1, thick, seg_len=seg_len)

    # 放射牆
    for r in range(rings):
        r0 = r_edges[r]
        r1 = r_edges[r + 1]
        for s in range(sectors):
            if cw_wall[r][s]:
                a = (s + 1) * dtheta
                add_radial_segment(walls, a, r0, r1, thick)

    return walls

# ----------------------------
# 碰撞（保留你的）
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

def collide_ball_with_segment(b, x1, y1, x2, y2, thick):
    px = b["x"]; py = b["y"]
    vx = x2 - x1; vy = y2 - y1
    wx = px - x1; wy = py - y1
    vv = vx*vx + vy*vy
    if vv == 0:
        return
    t = (wx*vx + wy*vy) / vv
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    cxp = x1 + t * vx
    cyp = y1 + t * vy

    dx = px - cxp
    dy = py - cyp
    d2 = dx*dx + dy*dy

    rad = b["r"] + (thick * 0.5)
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
# 三顆球狀態
# ----------------------------
balls = [
    {"x": CX - 25.0, "y": CY - 10.0, "vx": 0.0, "vy": 0.0, "r": 4, "c": c1},
    {"x": CX + 18.0, "y": CY + 12.0, "vx": 0.0, "vy": 0.0, "r": 3, "c": c2},
    {"x": CX +  5.0, "y": CY - 28.0, "vx": 0.0, "vy": 0.0, "r": 5, "c": c3},
]

def spawn_balls_in_first_ring():
    # 把球放在第一環中央（避免落在牆上），並清零速度
    dr = (MAZE_R_OUTER - MAZE_R_INNER) / MAZE_RINGS
    r_spawn = MAZE_R_INNER + dr * 0.55
    dtheta = 2 * math.pi / MAZE_SECTORS

    used = set()
    for b in balls:
        # 挑不同扇區，避免重疊
        s = rand_int(MAZE_SECTORS)
        while s in used:
            s = rand_int(MAZE_SECTORS)
        used.add(s)

        a = (s + 0.5) * dtheta
        x, y = polar_to_xy(r_spawn, a)

        b["x"] = x
        b["y"] = y
        b["vx"] = 0.0
        b["vy"] = 0.0

# ----------------------------
# 點一下重生迷宮（debounce）
# ----------------------------
last_tap_ms = 0
TAP_COOLDOWN_MS = 350

def is_tap():
    global last_tap_ms
    now = time.ticks_ms()

    # 方案A：Flag（最穩）
    try:
        if getattr(Touch, "Flag", 0) == 1:
            Touch.Flag = 0
            if time.ticks_diff(now, last_tap_ms) > TAP_COOLDOWN_MS:
                last_tap_ms = now
                return True
    except Exception:
        pass

    # 方案B：Gestures（如果你的 driver 有）
    try:
        g = getattr(Touch, "Gestures", 0)
        if g and time.ticks_diff(now, last_tap_ms) > TAP_COOLDOWN_MS:
            # 把任何手勢都當作一次互動（你只要點一下即可）
            Touch.Gestures = 0
            last_tap_ms = now
            return True
    except Exception:
        pass

    return False

# ----------------------------
# 迷宮全域資料
# ----------------------------
WALLS = []

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
    spawn_balls_in_first_ring()

# 先生成一次迷宮
regen_maze()

# ----------------------------
# 主迴圈
# ----------------------------
last_ms = time.ticks_ms()

while True:
    # 點一下就重生迷宮
    if is_tap():
        regen_maze()

    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000.0
    last_ms = now_ms
    if dt <= 0:
        dt = 0.01
    if dt > 0.05:
        dt = 0.05

    # 讀 IMU（一次）
    xg, yg, zg, gx, gy, gz = IMU.Read_XYZ()

    # 正規化
    gmag = math.sqrt(xg*xg + yg*yg + zg*zg)
    if gmag > 0:
        xg /= gmag
        yg /= gmag

    # 靜摩擦死區
    if abs(xg) < DEAD: xg = 0.0
    if abs(yg) < DEAD: yg = 0.0

    # 傾斜 -> 平面加速度（方向不對就改符號/互換）
    ax =  yg * ACC_SCALE
    ay = -xg * ACC_SCALE

    # 更新每顆球
    for b in balls:
        b["vx"] += ax * dt
        b["vy"] += ay * dt

        b["vx"] *= DAMP
        b["vy"] *= DAMP

        spd = math.sqrt(b["vx"]*b["vx"] + b["vy"]*b["vy"])
        if spd < 30:
            b["vx"] *= (1.0 - FRICTION)
            b["vy"] *= (1.0 - FRICTION)

        b["x"] += b["vx"] * dt
        b["y"] += b["vy"] * dt

        # 外圈
        collide_with_outer_circle(b)

        # 迷宮牆（線段）
        for (x1, y1, x2, y2, th) in WALLS:
            collide_ball_with_segment(b, x1, y1, x2, y2, th)

        # 再檢查一次外圈（避免被牆推出去）
        collide_with_outer_circle(b)

    # 繪圖
    LCD.fill_rect(0, 0, W, H, c_bg)
    draw_circle_ring(CX, CY, R_BOUND-1, c_ring)

    for (x1, y1, x2, y2, th) in WALLS:
        draw_thick_line(x1, y1, x2, y2, th, c_wall)

    for b in balls:
        runDot(b["r"], b["x"], b["y"], b["c"])

    LCD.show()
    time.sleep_ms(1)
