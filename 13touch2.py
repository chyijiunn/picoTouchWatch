import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
BG = color(0,0,0)
FG = color(255,255,255)
LCD.fill(FG)
LCD.show()

x= y = data = 0
color = 0
Touch.Flgh = 0
Touch.Flag = 0
Touch.Mode = 1
Touch.Set_Mode(Touch.Mode)

Touch.tim.init(period=1, callback=Touch.Timer_callback)

def Touch_HandWriting():
    x = y = data = 0
    color = 0
    Touch.Flgh = 0
    Touch.Flag = 0
    Touch.Mode = 1
    Touch.Set_Mode(Touch.Mode)
    
    LCD.fill(LCD.white)
    LCD.show()
    
    Touch.tim.init(period=1, callback=Touch.Timer_callback)

    while True:
        if Touch.Flgh == 0 and Touch.X_point != 0:
            Touch.Flgh = 1
            x = Touch.X_point
            y = Touch.Y_point
                
        if Touch.Flag == 1:
            time.sleep(0.001) #Prevent disconnection  防止断触
            if Touch.l < 100:           
                Touch.Flag = 0
                LCD.line(x,y,Touch.X_point,Touch.Y_point,color)
                LCD.Windows_show(x,y,Touch.X_point,Touch.Y_point)
                Touch.l=0
            else:
                Touch.Flag = 0
                LCD.pixel(Touch.X_point,Touch.Y_point,color)
                LCD.Windows_show(x,y,Touch.X_point,Touch.Y_point)
                Touch.l=0
        x = Touch.X_point
        y = Touch.Y_point
                        
Touch_HandWriting()

