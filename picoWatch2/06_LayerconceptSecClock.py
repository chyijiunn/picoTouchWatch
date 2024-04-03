import time
import touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

while 1:
    now = list(time.localtime())
    sec = now[5]#讀取秒數
    LCD.fill_rect(0,0,240,236-(4*sec),LCD.white)#更動時，上方白色往上
    LCD.fill_rect(0,236-(4*sec),240,4,0x180f)#更動時，下方綠色往上
    LCD.fill_rect(80,120,80,10,LCD.white)#維持數字更新
    LCD.text(str(sec),110,120,LCD.black)#最後疊上秒數

    LCD.show()
    time.sleep(1)