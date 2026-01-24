import hw , time

LCD = hw.LCD
Touch = hw.TP
color = LCD.color

c1 = color(55, 25, 125)
c2 = color(255, 225, 255)


Touch.Flag = 0
Touch.Set_Mode(1)

while True:
    if Touch.Flag == 1:
        x = Touch.X_point
        y = Touch.Y_point
        Touch.Flag = 0
        print(x,y)
        time.sleep(0.08)