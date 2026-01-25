import time, math
from hw import LCD, IMU

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

# 物理參數
ACC_SCALE = 880.0
DAMP = 0.995
FRICTION = 0.010
DEAD = 0.05

BOUNCE_WALL = 0.55     # 撞外圈反彈
BOUNCE_SEG  = 0.45     # 撞迷宮牆反彈（通常比外圈更不彈）
WALL_FRICTION = 0.88   # 撞牆後沿牆滑的摩擦（越小越黏）

# 迷宮牆：每條為 (x1,y1,x2,y2, thickness_px)
# 你可以用 LCD 座標直接畫。下面是一個示範迷宮（你可自行增刪調整）
WALLS = [
    # 橫向牆
    (60,  70, 180,  70, 5),
    (40, 120, 120, 120, 5),
    (120,150, 200,150, 5),
    # 直向牆
    (70,  70,  70, 170, 5),
    (150, 40, 150, 120, 5),
    (190,120, 190, 200, 5),
    # 斜牆（可做轉角）
    (60, 190, 110, 160, 5),
]

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
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        px = int(cx + r * math.cos(rad))
        py = int(cy + r * math.sin(rad))
        if 0 <= px < W and 0 <= py < H:
            LCD.pixel(px, py, col)

def draw_thick_line(x1, y1, x2, y2, thick, col):
    # 簡單加粗：沿法向偏移畫多條線（thick 小時足夠）
    dx = x2 - x1
    dy = y2 - y1
    L = math.sqrt(dx*dx + dy*dy)
    if L == 0:
        return
    nx = -dy / L
    ny =  dx / L
    half = thick // 2
    for k in range(-half, half+1):
        ox = int(nx * k)
        oy = int(ny * k)
        LCD.line(int(x1+ox), int(y1+oy), int(x2+ox), int(y2+oy), col)

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

# 球狀態
balls = [
    {"x": CX - 25.0, "y": CY - 10.0, "vx": 0.0, "vy": 0.0, "r": 4, "c": c1},
    {"x": CX + 18.0, "y": CY + 12.0, "vx": 0.0, "vy": 0.0, "r": 3, "c": c2},
    {"x": CX +  5.0, "y": CY - 28.0, "vx": 0.0, "vy": 0.0, "r": 5, "c": c3},
]

def collide_with_outer_circle(b):
    dx = b["x"] - CX
    dy = b["y"] - CY
    dist = math.sqrt(dx*dx + dy*dy)
    max_r = R_BOUND - b["r"]
    if dist > max_r and dist > 0:
        nx = dx / dist
        ny = dy / dist
        # 推回圈內
        b["x"] = CX + nx * max_r
        b["y"] = CY + ny * max_r
        # 反射速度（法向）
        vn = b["vx"]*nx + b["vy"]*ny
        b["vx"] = b["vx"] - (1.0 + BOUNCE_WALL) * vn * nx
        b["vy"] = b["vy"] - (1.0 + BOUNCE_WALL) * vn * ny
        b["vx"] *= 0.92
        b["vy"] *= 0.92

def collide_ball_with_segment(b, x1, y1, x2, y2, thick):
    # 球心到線段最短距離
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

    # 碰撞距離 = 球半徑 + 牆半厚
    rad = b["r"] + (thick * 0.5)
    if d2 >= rad*rad:
        return

    dist = math.sqrt(d2) if d2 > 0 else 0.0001
    nx = dx / dist
    ny = dy / dist

    # 推出重疊
    overlap = rad - dist
    b["x"] += nx * overlap
    b["y"] += ny * overlap

    # 反射速度（只對法向分量作用）
    vn = b["vx"]*nx + b["vy"]*ny
    if vn < 0:  # 只有在往牆內撞時才反彈
        b["vx"] = b["vx"] - (1.0 + BOUNCE_SEG) * vn * nx
        b["vy"] = b["vy"] - (1.0 + BOUNCE_SEG) * vn * ny
        # 沿牆摩擦（讓球更像貼牆滑）
        b["vx"] *= WALL_FRICTION
        b["vy"] *= WALL_FRICTION

last_ms = time.ticks_ms()

while True:
    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000.0
    last_ms = now_ms
    if dt <= 0:
        dt = 0.01
    if dt > 0.05:
        dt = 0.05

    # 讀 IMU（一次）
    xg, yg, zg, gx, gy, gz = IMU.Read_XYZ()

    # 正規化（避免瞬間加速度使得偏差變大）
    gmag = math.sqrt(xg*xg + yg*yg + zg*zg)
    if gmag > 0:
        xg /= gmag
        yg /= gmag

    # 靜摩擦死區：小傾角不滑
    if abs(xg) < DEAD: xg = 0.0
    if abs(yg) < DEAD: yg = 0.0

    # 傾斜 → 平面加速度
    # 若方向不對，改符號或互換 xg/yg
    ax =  yg * ACC_SCALE
    ay = -xg * ACC_SCALE

    # 更新每顆球
    for b in balls:
        # 速度積分
        b["vx"] += ax * dt
        b["vy"] += ay * dt

        # 阻尼
        b["vx"] *= DAMP
        b["vy"] *= DAMP

        # 低速摩擦（更容易停）
        spd = math.sqrt(b["vx"]*b["vx"] + b["vy"]*b["vy"])
        if spd < 30:
            b["vx"] *= (1.0 - FRICTION)
            b["vy"] *= (1.0 - FRICTION)

        # 位置積分
        b["x"] += b["vx"] * dt
        b["y"] += b["vy"] * dt

        # 先撞外圈
        collide_with_outer_circle(b)

        # 再撞迷宮牆（每條線段）
        for (x1, y1, x2, y2, th) in WALLS:
            collide_ball_with_segment(b, x1, y1, x2, y2, th)

        # 撞完牆後再檢查一次外圈（避免牆推擠讓球出圈）
        collide_with_outer_circle(b)

    # 繪圖（簡單起見每幀重畫）
    LCD.fill_rect(0, 0, W, H, c_bg)
    draw_circle_ring(CX, CY, R_BOUND-1, c_ring)

    # 畫迷宮牆
    for (x1, y1, x2, y2, th) in WALLS:
        draw_thick_line(x1, y1, x2, y2, th, c_wall)

    # 畫球
    for b in balls:
        runDot(b["r"], b["x"], b["y"], b["c"])

    LCD.show()
    time.sleep_ms(10)
