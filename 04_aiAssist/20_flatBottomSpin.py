import time, math
from hw import LCD, IMU

W, H = 240, 240
CX, CY = 120, 120

c = LCD.color(255, 255, 0)

# ===== 可調參數 =====
TIP_LEN   = 120   # 指針長度（尖端距離）
BASE_W    = 28    # 底端平邊寬度
BASE_BACK = 10    # 底邊中心往反方向退多少（讓根部更像「起始端」）
SLEEP_S   = 0.01
# ===================

while True:
    # 讀取重力
    xg = IMU.Read_XYZ()[0]
    yg = IMU.Read_XYZ()[1]

    # x0 = CX + TIP_LEN * yg
    # y0 = CY - TIP_LEN * xg
    # 這等價於方向向量 dir = (yg, -xg)
    dx = yg
    dy = -xg

    # 正規化，避免不同重力大小造成底邊歪/抖
    n = math.sqrt(dx*dx + dy*dy)
    if n < 1e-6:
        dx, dy = 0.0, -1.0   # 幾乎沒方向時給一個預設向上
    else:
        dx /= n
        dy /= n

    # 尖端
    x0 = int(CX + dx * TIP_LEN)
    y0 = int(CY + dy * TIP_LEN)

    # 底邊中心：往反方向退一點形成「起始端」
    bx = CX - dx * BASE_BACK
    by = CY - dy * BASE_BACK

    # 垂直向量（底邊方向），確保底端是「平直」且跟著旋轉
    px = -dy
    py =  dx

    hw = BASE_W * 0.5
    x1 = int(bx + px * hw)
    y1 = int(by + py * hw)
    x2 = int(bx - px * hw)
    y2 = int(by - py * hw)

    LCD.fill(0)
    LCD.fill_tri(x0, y0, x1, y1, x2, y2, c)
    LCD.show()
    time.sleep(SLEEP_S)
