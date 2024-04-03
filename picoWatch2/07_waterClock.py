import time
import touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

while 1:
    LCD.fill_rect(80,120,80,10,LCD.white)
    now = list(time.localtime())
    sec = now[5]
    LCD.fill_rect(0,0,240,236-(4*sec),LCD.white)
    LCD.fill_rect(0,236-(4*sec),240,240,0x180f)
    
    LCD.text(str(now[3])+':'+str(int(now[4])),100,120,LCD.black)#加上分、冒號在秒數前

    LCD.show()
    time.sleep(0.9)#為何是 0.9 ?0.5 or 0.4 可行否？