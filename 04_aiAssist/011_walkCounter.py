import time , touch
from machine import Timer
qmi8658=touch.QMI8658()
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)        
while True:
    yg = qmi8658.Read_XYZ()[1]	#define y axis gravity
    y = int(120 * (1 + yg ))		#define y of LCD
    LCD.pixel(120, y, c)			#draw a pixel
    LCD.scroll(-1,0)				#scroll whole screen
    print(yg)

    LCD.show()
    time.sleep(0.01)

