# 結合走路資料在外圈
import time , touch, math
LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(15535)
color = LCD.color

LCD.fill(color(255,225,0))

cx , cy =120 ,120 #center of watch
NUM = 0
TARGET = 100#每天要走幾步

def runDotRing(reach , spinLen , color):
    r = 12
    x = int(spinLen*math.sin(math.radians(reach*360)))
    y = int(spinLen*math.cos(math.radians(reach*360)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
while 1:
    xyz=qmi8658.Read_XYZ()
    N1 = xyz[5]
    now = list(time.gmtime())
    LCD.write_text('{0:0>2}:{1:0>2}:{2:0>2}'.format(now[3],now[4],now[5]),60,160,2,color(255,225,0))
    LCD.show()
    xyz=qmi8658.Read_XYZ()
    N2 = xyz[5]
    if N1*N2 < 0:
        NUM = NUM + 1
    reach = NUM/TARGET
    colorfactor = int(255*(1-reach))
    runDotRing(reach,110,color(colorfactor,200,colorfactor))
    
