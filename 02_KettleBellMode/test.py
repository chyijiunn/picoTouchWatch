import touch#上傳 lib 至 pico，內含touch.py, 並引入 touch
LCD = touch.LCD_1inch28()#touch 中的 LCD 類別引入
LCD.set_bl_pwm(15535)#設定亮度~65535

LCD.fill_rect(120,120,20,-40,LCD.red)#畫一個長方形，從0,0開始，大小為240 ,40，並設定顏色LCD.red , green ,blue, yellow , magenta ,cyan ,white , black
LCD.text("JustTry",90,25,LCD.white)#寫一個字，位置是110,25,顏色是黑色,可至lib/touch.py 38 line 新增顏色
LCD.show()#讓上面呈現出來