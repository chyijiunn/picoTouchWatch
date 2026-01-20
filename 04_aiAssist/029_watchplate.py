import time, math, touch

LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(15535)

# =========================
# 基本參數
# =========================
cx, cy = 70, 70
platesize = 40

BG = color(0, 0, 0)

# 刻度設定
tickmark_h = platesize - 6
tickmark_m = platesize - 2
tickmark_h_color = color(255, 120, 0)
tickmark_m_color = color(120, 120, 120)

# 指針設定
hour_len = platesize * 0.5
min_len  = platesize * 0.8
sec_len  = platesize * 0.9

hour_color = color(250, 50, 125)
min_color  = color(200,100,  0)
sec_color  = color(250,225,  0)

# =========================
# 畫錶盤（一次）
# =========================
def draw_plate():
    LCD.fill(BG)

    # 分刻度
    for i in range(60):
        ang = math.radians(6 * i)
        LCD.line(
            cx + int(tickmark_m * math.sin(ang)),
            cy - int(tickmark_m * math.cos(ang)),
            cx + int(platesize  * math.sin(ang)),
            cy - int(platesize  * math.cos(ang)),
            tickmark_m_color
        )

    # 時刻度
    for i in range(12):
        ang = math.radians(30 * i)
        LCD.line(
            cx + int(tickmark_h * math.sin(ang)),
            cy - int(tickmark_h * math.cos(ang)),
            cx + int(platesize  * math.sin(ang)),
            cy - int(platesize  * math.cos(ang)),
            tickmark_h_color
        )

# =========================
# 三角形指針
# =========================
def spin_tri(angle, base_w, length, c):
    bx = int(base_w * math.sin(math.radians(angle + 90)))
    by = int(base_w * math.cos(math.radians(angle + 90)))
    tx = int(length * math.sin(math.radians(angle)))
    ty = int(length * math.cos(math.radians(angle)))

    LCD.fill_tri(
        cx + tx, cy - ty,
        cx + bx, cy - by,
        cx - bx, cy + by,
        c
    )

# =========================
# 主錶更新
# =========================
def draw_watch():
    now = time.localtime()
    h = now[3] % 12

    hour_ang = 30 * h + 0.5 * now[4]
    min_ang  = 6 * now[4] + 0.1 * now[5]
    sec_ang  = 6 * now[5]

    # 畫
    spin_tri(hour_ang, 4, hour_len, hour_color)
    spin_tri(min_ang,  3, min_len,  min_color)

    sx = int(sec_len * math.sin(math.radians(sec_ang)))
    sy = int(sec_len * math.cos(math.radians(sec_ang)))
    LCD.line(cx, cy, cx + sx, cy - sy, sec_color)

    LCD.show()

    # 擦（只擦指針）
    spin_tri(hour_ang, 4, hour_len, BG)
    spin_tri(min_ang,  3, min_len,  BG)
    LCD.line(cx, cy, cx + sx, cy - sy, BG)

# =========================
# 執行
# =========================
draw_plate()

while True:
    draw_watch()
    time.sleep(1)
