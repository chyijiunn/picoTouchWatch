import time , touch, math , random
from machine import Timer
qmi8658=touch.QMI8658()
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
        
while True:
    LCD.fill(LCD.black)#螢幕刷新
    xyz=qmi8658.Read_XYZ()
    x0 = round(xyz[0],1)#讀取x ,z 的傾角，並取到小數下一位
    y0 = round(xyz[1],1)
    
    time.sleep(0.01)
    
    xyz=qmi8658.Read_XYZ()
    x1 = round(xyz[0],1)#再讀取x ,z 的傾角
    y1 = round(xyz[1],1)
    
    if x1 == x0 and y1 == y0:#若兩者相同，則顯示安全
        LCD.text("Safe",100,120,LCD.white)
        LCD.show()
    else:#不然就爆炸
        LCD.fill(LCD.white)
        LCD.show()
        time.sleep(0.1)
        LCD.fill(LCD.red)
        LCD.show()
        time.sleep(0.1)

