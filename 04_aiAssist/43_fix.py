import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)
c1 = LCD.color(255,0,0)

t0 = time.ticks_ms()

def runDot(r , x , y , color):
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(x+i,y+j,color)

def zeroArea(r,color):
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(120+i,120+j,color)
            if i*i + j*j <= (r-3)*(r-3):
                LCD.pixel(120+i,120+j,0)

def rack(sec):
    global t0  # 关键：告诉 Python 这里用的是全域 t0（且会更新它）

    # 是否在 40x40 的中心区域（你原本的判定方式）
    in_box = ((x-120)*(x-120) < 40*40) and ((y-120)*(y-120) < 40*40)

    if in_box:
        # ticks_diff 比直接相减更稳（可处理 ticks 回捲）
        t = time.ticks_diff(time.ticks_ms(), t0) // 1000
        if t > sec:
            t = sec
    else:
        t0 = time.ticks_ms()
        t = 0

    LCD.write_text(str(t), 100, 200, 3, c)

while True:
    yg = IMU.Read_XYZ()[1]
    xg = IMU.Read_XYZ()[0]
    if yg > 1: yg =  1
    if yg <-1: yg = -1
    if xg > 1: xg =  1
    if xg <-1: xg = -1

    y = 120 - int(120 * xg)
    x = 120 + int(120 * yg)

    LCD.fill(0)
    runDot(5 , x , y , c)
    zeroArea(40,c)
    rack(60)

    LCD.show()
    time.sleep(0.3)
