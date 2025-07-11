#新增 list ，超過某數量刪除前面紀錄點
from machine import Pin, PWM
from utime import sleep
import touch , _thread
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
Touch.tim.init(period=1, callback=Touch.Timer_callback)
Touch.Flag = 0
LCD.fill(color(0,0,0))
position = []
def shoot(x,y):
    shootsize = 20
    for j in range(y/shootsize):
        for i in range(shootsize):
            LCD.vline(x,y-(shootsize*j),shootsize,color(150,150,20))
            LCD.show()
        for i in range(shootsize):
            LCD.vline(x,y-(shootsize*j),shootsize,color(0,0,0))       
        
while 1:
    if Touch.Flag == 1:
        x , y = Touch.X_point , Touch.Y_point
        position.append([x,y])
        print(position)
        Touch.Flag = 0
        if len(position)>=3:del position[-3:]
        sleep(0.05)
 


