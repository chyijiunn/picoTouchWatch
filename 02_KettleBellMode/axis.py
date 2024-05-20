import touch,utime
LCD = touch.LCD_1inch28()

LCD.set_bl_pwm(20000)#亮度~65535
qmi8658=touch.QMI8658()

while True:
    xyz=qmi8658.Read_XYZ()
    print(xyz[0]) #xyz[] from 0~6
    utime.sleep(0.1)
    