import time , touch , math #數學用法
from machine import Timer
qmi8658=touch.QMI8658()
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)    
while True:
    yg = qmi8658.Read_XYZ()[1]
    if yg > 1: yg =  1	
    if yg <-1: yg = -1
    degree = math.degrees(math.asin(yg))
    
    y = int(120 * (1 + yg ))
    
    LCD.fill_rect(120,100,120,40,c0 )#refresh
    LCD.write_text(str(degree),120,100,3,c) #(str , x , y , color )
    
    #print(degree)

    LCD.show()
    time.sleep(0.01)


