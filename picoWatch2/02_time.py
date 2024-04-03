import utime , touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

LCD.fill_rect(0,0,240,40,LCD.red)
LCD.text("Now",110,25,LCD.white)
LCD.show()

now = utime.localtime()#讀取電腦端時間
LCD.text(str(now),0,120,LCD.black)#把剛剛時間寫入LCD
'''
(2024, 4, 3, 16, 6, 57, 2, 94) 代表年月日時分秒,Mon = 0 , 年初到今天過了幾天
'''
print(now)
LCD.show()