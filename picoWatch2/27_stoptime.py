# 做一個碼錶，利用 utime.ticks_ms() 讀取毫秒資料
# 中間間隔一秒後再讀第二次，兩者時間相減，顯示出毫秒差異於錶面
import touch , machine ,utime

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
qmi8658=touch.QMI8658()

LCD.fill_rect(0,0,240,40,LCD.red)
LCD.text("Now",110,25,LCD.white)
LCD.show()

#讀取毫秒數，https://docs.singtown.com/micropython/zh/latest/openmvcam/library/utime.html
N1 = utime.ticks_ms()
utime.sleep(1)
N2 = utime.ticks_ms()
print(type(N1))
LCD.text(str(N2-N1),100,120,LCD.black)#注意 text 必須為 string
LCD.show()