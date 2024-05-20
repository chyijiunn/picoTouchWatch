import touch,utime,math
LCD = touch.LCD_1inch28()

LCD.set_bl_pwm(20000)#亮度~65535
qmi8658=touch.QMI8658()
N1 = utime.ticks_ms()
color = LCD.color
c1 = color(255,255,255)
data = open('record.csv','a')

while True:
    try:
        a=qmi8658.Read_XYZ()
        data.write(str((utime.ticks_ms()-N1)/1000) + ','+ str(a[4])+','+ str(a[0])+'\n')

    except KeyboardInterrupt:
        data.close()
        break
        
    
    