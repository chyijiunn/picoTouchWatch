import touch,utime,math
LCD = touch.LCD_1inch28()

LCD.set_bl_pwm(0)#亮度~65535
qmi8658=touch.QMI8658()

while True:
    a=qmi8658.Read_XYZ()[0]
    print(a) 
    utime.sleep(0.1)
    