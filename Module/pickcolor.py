import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color
LCD.set_bl_pwm(5535)

def pickcolor():
    x = y  = 0
    Touch.Flgh = 0
    Touch.Flag = 0
    Touch.Set_Mode(2)
    LCD.fill(LCD.white)
    LCD.show()
    Touch.tim.init(period=1000, callback=Touch.Timer_callback)
    while True:
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            return x , y
            break
    
while pickcolor() != 0:
    print(pickcolor())
    break
    