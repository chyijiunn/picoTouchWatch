import hw , time

LCD = hw.LCD
Touch = hw.TP

# 設定為混合模式 (Mode 2)
Touch.Set_Mode(2)
Touch.Mode = 2
Touch.Flag = 0
Touch.Gestures = 0 # 初始化手勢變數

print("Mode 2 (Mixed) Started...")

while True:
    if Touch.Flag == 1:
        # 1. 檢查是否有手勢 (0x00 代表無手勢)
        # CST816T 手勢對照: 0x01:上滑, 0x02:下滑, 0x03:左滑, 0x04:右滑, 0x0B:雙擊, 0x0C:長按
        if Touch.Gestures != 0x00:
            print(f"Gesture Detected: {hex(Touch.Gestures)}")
        
        # 2. 顯示座標
        print(f"Point: X={Touch.X_point}, Y={Touch.Y_point}")
        
        # 3. 清除 Flag 與 Gestures 以等待下次輸入
        Touch.Flag = 0
        Touch.Gestures = 0
        
    time.sleep(0.05)