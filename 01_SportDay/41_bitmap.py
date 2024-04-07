import touch , bmp #記得引入 bmp
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(12000)
color = LCD.color

LCD.fill(color(255,255,0))
LCD.show()
# LCD.bitmap(檔名.py,起始 x ,起始 y)
LCD.bitmap(bmp,90,90)
