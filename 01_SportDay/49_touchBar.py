import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
BG = color(0,0,0)
FG = color(255,255,255)
c1 = color(55,25,125)
c2 = color(255,225,255)
LCD.fill(BG)


xstart,ystart,xlen,ylen = 80,160 , 80 , 20


def scrollBar():
    x = y = data = 0
    color = 0
    Touch.Flgh = 0
    Touch.Flag = 0
    Touch.Mode = 1
    Touch.Set_Mode(Touch.Mode)

    while True:
        LCD.fill_rect(xstart,ystart,xlen,ylen,c1)
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            if x-xstart > xlen: x = xstart + xlen
            LCD.fill_rect(xstart,ystart,x-xstart,ylen,c2)
            LCD.show()
            print(x,y)
'''
        if Touch.Flag == 1:
            if (Touch.X_point > 0 and Touch.X_point < 240) and (Touch.Y_point > 0 and Touch.Y_point < 240):Touch.Flgh = 3
            else:Touch.Flgh = 4
                    
            if Touch.Flgh == 3:
                time.sleep(0.005) #Prevent disconnection
                if Touch.l < 25: #小於此值畫線
                    Touch.Flag = 0
                    LCD.line(x,y,Touch.X_point,Touch.Y_point,color)
                    LCD.Windows_show(x,y,Touch.X_point,Touch.Y_point)
                    Touch.l=0
                else:#否則畫點
                    Touch.Flag = 0
                    LCD.pixel(Touch.X_point,Touch.Y_point,color)
                    LCD.Windows_show(x,y,Touch.X_point,Touch.Y_point)
                    print(Touch.l,'2')
                    Touch.l=0
                        
                x = Touch.X_point
                y = Touch.Y_point
'''
scrollBar()

