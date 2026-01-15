import time , touch
from machine import Timer
qmi8658=touch.QMI8658()#引入六軸
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
C0 = LCD.color(0,0,0)
N = 0
while True:
    z1 = qmi8658.Read_XYZ()[5]/500
    y = int(120 * z1)
    LCD.line(120,120,120, 120+y, c)
    LCD.scroll(-1,0)
    z2 = qmi8658.Read_XYZ()[5]/500
    if (y*y > 9) and (z1*z2<0): N = N + 1
    
    LCD.fill_rect(160,100,40,40,C0 )
    LCD.write_text(str(N),160 ,100,3,c)
    LCD.show()
    time.sleep(0.1)



