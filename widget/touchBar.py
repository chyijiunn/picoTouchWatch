# touchBar.py
import time, random, math , hw , touch

LCD = hw.LCD
Touch = hw.TP
color = LCD.color

BG = color(0, 0, 0)
FG = color(255, 255, 255)
c1 = color(55, 25, 125)
c2 = color(255, 225, 255)

xstart, ystart, xlen, ylen = 80, 60, 80, 20
LCD.fill(BG)

def scrollBar():
    Touch.Flag = 0
    Touch.Set_Mode(1)

    LCD.fill(BG)
    LCD.write_text('Slide!', 40, 120, 4, c1)
    LCD.show()

    while True:
        LCD.fill_rect(xstart, ystart, xlen, ylen, c1)
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            if x-xstart > xlen: x = xstart + xlen
            LCD.fill_rect(xstart, ystart, x - xstart, ylen, c2)
            LCD.show()
            #time.sleep(0.08)
            Touch.Flag = 0
            print(x,y)
         
scrollBar()