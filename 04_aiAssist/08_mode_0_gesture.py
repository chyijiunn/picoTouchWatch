import hw , time

LCD = hw.LCD
Touch = hw.TP

# 設定為gesture模式 (Mode 0)
Touch.Set_Mode(0)
Touch.Mode = 0

Touch.Flag = 0
Touch.Gestures = 0 # 初始化手勢變數

print("TouchMode 0 Started...")
while True:
    if Touch.Flag == 1:
        # 讀取到的手勢不為 0 才印出
        if Touch.Gestures != 0x00:
            # 為了方便閱讀，可以印出對應動作
            g = Touch.Gestures
            action = "Unknown"
            if g == 0x01: action = "Slide UP"
            elif g == 0x02: action = "Slide DOWN"
            elif g == 0x03: action = "Slide LEFT"
            elif g == 0x04: action = "Slide RIGHT"
            elif g == 0x0B: action = "Double Click"
            elif g == 0x0C: action = "Long Press"
            
            print(f"Gesture: {hex(g)} ({action})")
            
            # 清除手勢暫存，避免重複判斷
            Touch.Gestures = 0
            
        # 清除 Flag 等待下次中斷
        Touch.Flag = 0
        
    time.sleep(0.05)