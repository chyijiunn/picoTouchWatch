import hw , time

LCD = hw.LCD
Touch = hw.TP
color = LCD.color

c = color(255,255,0)
LCD.fill(0)
LCD.show()
# 設定為混合模式 (Mode 2)
Touch.Set_Mode(2)
Touch.Mode = 2
Touch.Flag = 0
Touch.Gestures = 0 # 初始化手勢變數

print("Mode 2 (Mixed) Started...")

while True:
    LCD.fill(0)
    if Touch.Flag == 1:
        if Touch.Gestures != 0x00:
            g = Touch.Gestures
            action = "Unknown"
            x = Touch.X_point
            y = Touch.Y_point
            
            if g == 0x01: action = "Slide UP"
            elif g == 0x02: action = "Slide DOWN"
            elif g == 0x03: action = "Slide LEFT"
            elif g == 0x04: action = "Slide RIGHT"
            elif g == 0x0B: action = "Double Click"
            elif g == 0x0C: action = "Long Press"
            
            LCD.write_text(str(x)+' '+str(y),80,60,2,c)
            LCD.write_text(action, 10,110,3,c)
            LCD.show()
            Touch.Gestures = 0
            
        Touch.Flag = 0
        
        
        
    time.sleep(0.05)
