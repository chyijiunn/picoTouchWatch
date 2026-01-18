import time, math
from hw import LCD, IMU

# 顏色
c_bg   = LCD.color(0, 0, 0)
c_ring = LCD.color(40, 40, 40)
c1 = LCD.color(255, 255, 0)
c2 = LCD.color(0, 220, 160)
c3 = LCD.color(255, 80, 80)

# 盤面設定
W, H = 240, 240
CX, CY = 120, 120
R_BOUND = 120

# 物理參數（可調）
ACC_SCALE = 880.0     # 傾斜重力 → 像素/秒^2
DAMP = 0.995          # 空氣阻尼
FRICTION = 0.010      # 低速摩擦
BOUNCE_WALL = 0.55    # 撞牆反彈係數
BOUNCE_BALL = 0.85    # 球球反彈係數（越大越彈）
DEAD = 0.05           # 靜摩擦死區（傾斜很小就不動）

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

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

# 三顆球（半徑可不同）
balls = [
    {"x": CX - 25.0, "y": CY - 10.0, "vx": 0.0, "vy": 0.0, "r": 4, "c": c1},
    {"x": CX + 18.0, "y": CY + 12.0, "vx": 0.0, "vy": 0.0, "r": 3, "c": c2},
    {"x": CX +  5.0, "y": CY - 28.0, "vx": 0.0, "vy": 0.0, "r": 5, "c": c3},
]

last_ms = time.ticks_ms()

while True:
    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000.0
    last_ms = now_ms
    if dt <= 0:
        dt = 0.01
    if dt > 0.05:
        dt = 0.05

    # 讀 IMU（一次就好）
    xg, yg, zg, gx, gy, gz = IMU.Read_XYZ()

    # 正規化（避免動作時 gmag != 1 造成爆衝）
    gmag = math.sqrt(xg*xg + yg*yg + zg*zg)
    if gmag > 0:
        xg /= gmag
        yg /= gmag

    # 靜摩擦死區（讓小傾角不滑）
    if abs(xg) < DEAD: xg = 0.0
    if abs(yg) < DEAD: yg = 0.0

    # 傾斜造成的平面加速度
    # 若方向顛倒，就改符號或互換 xg/yg
    ax =  yg * ACC_SCALE
    ay = -xg * ACC_SCALE

    # ---- 更新每顆球 ----
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

        # 撞圓形邊界（各自半徑不同）
        dx = b["x"] - CX
        dy = b["y"] - CY
        dist = math.sqrt(dx*dx + dy*dy)
        max_r = (R_BOUND - b["r"])
        if dist > max_r and dist > 0:
            nx = dx / dist
            ny = dy / dist

            # 推回邊界上
            b["x"] = CX + nx * max_r
            b["y"] = CY + ny * max_r

            # 速度反射
            vn = b["vx"]*nx + b["vy"]*ny
            b["vx"] = b["vx"] - (1.0 + BOUNCE_WALL) * vn * nx
            b["vy"] = b["vy"] - (1.0 + BOUNCE_WALL) * vn * ny

            # 牆面摩擦
            b["vx"] *= 0.92
            b["vy"] *= 0.92

    # ---- 球球碰撞（3 顆球成本很低）----
    # 簡化：同質量、只處理法向分量，並解重疊
    n = len(balls)
    for i in range(n):
        for j in range(i+1, n):
            bi = balls[i]
            bj = balls[j]
            dx = bj["x"] - bi["x"]
            dy = bj["y"] - bi["y"]
            dist = math.sqrt(dx*dx + dy*dy)
            min_d = bi["r"] + bj["r"]

            if dist > 0 and dist < min_d:
                nx = dx / dist
                ny = dy / dist

                # 先把重疊推出去（一人一半）
                overlap = (min_d - dist)
                bi["x"] -= nx * overlap * 0.5
                bi["y"] -= ny * overlap * 0.5
                bj["x"] += nx * overlap * 0.5
                bj["y"] += ny * overlap * 0.5

                # 交換/修正法向速度（等質量彈性碰撞的簡化版）
                vix, viy = bi["vx"], bi["vy"]
                vjx, vjy = bj["vx"], bj["vy"]

                vi_n = vix*nx + viy*ny
                vj_n = vjx*nx + vjy*ny

                # 相對速度若正在分離就不處理
                if (vj_n - vi_n) < 0:
                    # 彈性係數
                    e = BOUNCE_BALL
                    # 等質量：法向分量交換並帶 e
                    vi_n_new = vj_n * e
                    vj_n_new = vi_n * e

                    bi["vx"] += (vi_n_new - vi_n) * nx
                    bi["vy"] += (vi_n_new - vi_n) * ny
                    bj["vx"] += (vj_n_new - vj_n) * nx
                    bj["vy"] += (vj_n_new - vj_n) * ny

    # ---- 繪圖 ----
    LCD.fill_rect(0, 0, W, H, c_bg)
    draw_circle_ring(CX, CY, R_BOUND-1, c_ring)

    for b in balls:
        runDot(b["r"], b["x"], b["y"], b["c"])

    LCD.show()
    time.sleep_ms(10)
