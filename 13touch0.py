import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
BG = color(0,0,0)
FG = color(255,255,255)
LCD.fill(FG)
LCD.show()

def Touch_HandWriting():
    x = y = data = 0
    color = 0
    Touch.Flgh = 0
    Touch.Flag = 0
    Touch.Mode = 1
    Touch.Set_Mode(Touch.Mode)
    
    LCD.fill(LCD.white)
    LCD.rect(0, 0, 35, 208,LCD.red,True)
    LCD.rect(0, 0, 208, 35,LCD.green,True)
    LCD.rect(205, 0, 240, 240,LCD.blue,True)
    LCD.rect(0, 205, 240, 240,LCD.brown,True)
    LCD.show()
    
    Touch.tim.init(period=1, callback=Touch.Timer_callback)

    while True:
        if Touch.Flgh == 0 and Touch.X_point != 0:
            Touch.Flgh = 1
            x = Touch.X_point
            y = Touch.Y_point
                
        if Touch.Flag == 1:
            if (Touch.X_point > 34 and Touch.X_point < 205) and (Touch.Y_point > 34 and Touch.Y_point < 205):Touch.Flgh = 3
            else:
                if (Touch.X_point > 0 and Touch.X_point < 33) and (Touch.Y_point > 0 and Touch.Y_point < 208):color = LCD.red
                if (Touch.X_point > 0 and Touch.X_point < 208) and (Touch.Y_point > 0 and Touch.Y_point < 33):color = LCD.green     
                if (Touch.X_point > 208 and Touch.X_point < 240) and (Touch.Y_point > 0 and Touch.Y_point < 240):color = LCD.blue                        
                if (Touch.X_point > 0 and Touch.X_point < 240) and (Touch.Y_point > 208 and Touch.Y_point < 240):
                    LCD.fill(LCD.white)
                    LCD.rect(0, 0, 35, 208,LCD.red,True)
                    LCD.rect(0, 0, 208, 35,LCD.green,True)
                    LCD.rect(205, 0, 240, 240,LCD.blue,True)
                    LCD.rect(0, 205, 240, 240,LCD.brown,True)
                    LCD.show()
                Touch.Flgh = 4
                    
            if Touch.Flgh == 3:
                time.sleep(0.001) #Prevent disconnection  防止断触
                if Touch.l < 25:           
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