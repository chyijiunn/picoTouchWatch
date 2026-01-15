import time , touch
from machine import Timer
qmi8658=touch.QMI8658()#引入六軸
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)        
while True:
    z_a = qmi8658.Read_XYZ()[5]/500
    y = int(120 * z_a)
    LCD.line(120,120,120, 120+y, c)
    LCD.scroll(-1,0)
    print(y)

    LCD.show()
    time.sleep(0.1)


