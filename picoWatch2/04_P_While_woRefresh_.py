import time
import touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

LCD.fill_rect(0,0,240,40,LCD.red)
LCD.text("Now",110,25,LCD.white)
LCD.show()
while 1:#一直不斷重複
    now = list(time.localtime())
    LCD.text(str(now[3:6]),80,120,LCD.black)
    LCD.show()
    time.sleep(1)#暫停一秒，這邊的停頓是是指一秒跳一次嗎？

#還有額外的問題
