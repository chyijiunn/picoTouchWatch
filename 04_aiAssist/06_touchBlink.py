import hw , time
LCD = hw.LCD
Touch = hw.TP

c = LCD.color(255, 0, 0)

Touch.Flag = 0
Touch.Set_Mode(1)
LCD.fill(0)
LCD.show()

while True:
    if Touch.Flag == 1:
        LCD.write_text('I am touch!',5,110,3,c)
        LCD.show()
        Touch.Flag = 0
    else:
        LCD.fill_rect(5,110,240,24,0)
        LCD.show()
    
    time.sleep(0.1)