# 錶面和時間結合在一起
import time , touch, math
LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(30000)
color = LCD.color

LCD.fill(color(255,225,0))

while 1:
    now = list(time.gmtime())
    #LCD._text16(font,str(now[3])+':'+str(now[4])+':'+str(now[5]),60,160,color(0,0,0),color(255,225,0))
    LCD.write_text('{0:0>2}:{1:0>2}:{2:0>2}'.format(now[3],now[4],now[5]),60,160,2,color(255,225,0))
    LCD.show
