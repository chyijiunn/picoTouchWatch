# 將運動資料轉為圖形化介面，用上次的紅點秒針，
# 改為繞行，但不刷新螢幕，可以填滿外圈
import time , touch, math

LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(15535)
color = LCD.color
cx , cy =120 ,120 #center of watch
NUM = 0
TARGET = 100#一天行走的目標
                
def runDotRing(tic , spinLen , color):
    r = 12
    # NUM/TARGET 行走目標百分比*360即佔一個圈的角度
    # 轉弧度回來，再 sin、之後轉給 x 座標用
    x = int(spinLen*math.sin(math.radians(NUM/TARGET*360)))
    y = int(spinLen*math.cos(math.radians(NUM/TARGET*360)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)

while 1:
    xyz=qmi8658.Read_XYZ()
    N1 = xyz[5]
    time.sleep(0.25)
    xyz=qmi8658.Read_XYZ()
    N2 = xyz[5]
    if N1*N2 < 0:NUM=NUM+1
    runDotRing(NUM,110,color(250,30,60))#紅點繞行秒針
    LCD.show()

