import utime,touch

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(0)
qmi8658=touch.QMI8658()

ori_x = 120
ori_y = 120
N1 = utime.ticks_ms()

while True:
    xyz=qmi8658.Read_XYZ()
    for i in range(3,6,1):
        print(round(xyz[i],2),'',end ='')
    print()
    utime.sleep(0.4)
