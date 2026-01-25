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
            if i*i + j*j <= r*r:LCD.pixel(x+i,y+j,color)

def zeroArea(r,color):
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(120+i,120+j,color)
            if i*i + j*j <= (r-3)*(r-3):
                LCD.pixel(120+i,120+j,0)

def read_record():
    try:
        with open("rackrecord", "r") as f:
            return int(f.read().strip())
    except:
        return 0

def write_record(value):
    with open("rackrecord", "w") as f:
        f.write(str(value))

def rack(sec):
    global t0, record
    in_box = ((x-120)*(x-120) < 40*40) and ((y-120)*(y-120) < 40*40)
    if in_box:
        t = time.ticks_diff(time.ticks_ms(), t0) // 1000
        #if t >= sec:
    else:
        t0 = time.ticks_ms()
        t = 0
    
    # 更新紀錄
    if t > record:
        record = t
        write_record(record)
        
    LCD.write_text(str(t), 100, 200, 3, c)# 目前時間
    LCD.write_text("max", 105, 20, 1, c)# 顯示最高
    LCD.write_text(str(record), 110, 40, 2, c)


        
record = read_record()

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



