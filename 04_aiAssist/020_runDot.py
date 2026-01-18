import time, touch, math

qmi8658 = touch.QMI8658()
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
c_ball = LCD.color(255,255,0)
c_bg   = LCD.color(0,0,0)
c_ring = LCD.color(40,40,40)

CX, CY = 120, 120
R_BOUND = 120          # 邊界半徑
R_BALL  = 3            # 球半徑（像素）

# 物理參數（你可以調）
ACC_SCALE = 880.0      # 把 g 單位轉成 像素/秒^2 的比例
DAMP = 0.985           # 空氣阻尼（越小越黏）
FRICTION = 0.010       # 近似摩擦（速度越小越容易停）
BOUNCE = 0.85          # 反彈係數（0~1，越小越不彈）

# 小球狀態（用 float 才會順）
x = float(CX)
y = float(CY)
vx = 0.0
vy = 0.0

def runDot(r, x, y, color):
    x = int(x); y = int(y)
    for i in range(-r, r+1):
        for j in range(-r, r+1):
            if i*i + j*j <= r*r:
                xi = x+i; yj = y+j
                if 0 <= xi < 240 and 0 <= yj < 240:
                    LCD.pixel(xi, yj, color)

def draw_circle_ring(cx, cy, r, col):
    # 粗略畫圓環（每幀畫一次也OK；要省電可降低頻率）
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        px = int(cx + r * math.cos(rad))
        py = int(cy + r * math.sin(rad))
        if 0 <= px < 240 and 0 <= py < 240:
            LCD.pixel(px, py, col)

last_ms = time.ticks_ms()

while True:
    now_ms = time.ticks_ms()
    dt = time.ticks_diff(now_ms, last_ms) / 1000.0
    last_ms = now_ms
    if dt <= 0:
        dt = 0.01
    if dt > 0.05:       # 防止偶發卡頓導致飛出去
        dt = 0.05

    # 讀 IMU（一次就好）
    xg, yg, zg, gx, gy, gz = qmi8658.Read_XYZ()

    # 建議做正規化：避免動作時 gmag != 1 造成爆衝
    gmag = math.sqrt(xg*xg + yg*yg + zg*zg)
    if gmag > 0:
        xg /= gmag
        yg /= gmag

    # 把傾斜映射到「盤面加速度」
    # 注意：哪一軸對應螢幕 x/y 方向可能要互換或取負號
    ax =  yg * ACC_SCALE     # 螢幕向右為正
    ay = -xg * ACC_SCALE     # 螢幕向下為正（所以用 -xg）

    # 速度更新（加速度積分）
    vx += ax * dt
    vy += ay * dt

    # 阻尼（空氣阻力）
    vx *= DAMP
    vy *= DAMP

    # 近似摩擦：速度越小越容易停
    spd = math.sqrt(vx*vx + vy*vy)
    if spd < 30:  # 低速時加強摩擦
        vx *= (1.0 - FRICTION)
        vy *= (1.0 - FRICTION)

    # 位置更新（速度積分）
    x += vx * dt
    y += vy * dt

    # 圓形邊界碰撞（考慮球半徑）
    dx = x - CX
    dy = y - CY
    dist = math.sqrt(dx*dx + dy*dy)
    max_r = R_BOUND - R_BALL

    if dist > max_r and dist > 0:
        # 把球推回圓內（投影到邊界上）
        nx = dx / dist
        ny = dy / dist
        x = CX + nx * max_r
        y = CY + ny * max_r

        # 速度對法向量反射（並加反彈係數）
        vn = vx*nx + vy*ny              # 法向速度分量
        vx = vx - (1.0 + BOUNCE) * vn * nx
        vy = vy - (1.0 + BOUNCE) * vn * ny

        # 碰撞摩擦：沿切線方向也略衰減，避免一直貼邊抖
        vx *= 0.92
        vy *= 0.92

    # 繪圖
    LCD.fill_rect(0, 0, 240, 240, c_bg)
    draw_circle_ring(CX, CY, R_BOUND-1, c_ring)
    runDot(R_BALL, x, y, c_ball)

    LCD.show()
    time.sleep_ms(5)
