# 練習六軸的資料，看數值變化與方向的關聯性，
import touch#引入寫好的
LCD = touch.LCD_1inch28()

LCD.set_bl_pwm(3000)#亮度~65535
qmi8658=touch.QMI8658()

while True:
    xyz=qmi8658.Read_XYZ()
    print(xyz[5])#xyz[] from 0~6