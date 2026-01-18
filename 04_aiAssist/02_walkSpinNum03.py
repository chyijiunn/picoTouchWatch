import time , touch , math #數學用法
from machine import Timer
qmi8658=touch.QMI8658()
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)

while True:
    yg = qmi8658.Read_XYZ()[1]
    xg = qmi8658.Read_XYZ()[0]
    if yg > 1: yg =  1
    if yg <-1: yg = -1
    if xg > 1: xg =  1
    if xg <-1: xg = -1

    y = 120 - int(120 * xg)
    x = 120 + int(120 * yg)
    
    LCD.fill_rect(0,0,240,240,c0 )
    LCD.line(120,120,x,y,c)

    LCD.show()
    time.sleep(0.01)



