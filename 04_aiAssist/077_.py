# 075_runballsMazeRound_Optimized.py
# 針對 RP2040 + Waveshare 1.28" Round LCD 的優化版本
# 主要改進：
# 1. 使用局部刷新 (Partial Refresh) 取代全屏刷新，大幅提升 FPS
# 2. 移除 types 模組依賴，修正 ImportError
import time, math, gc ,lcd_optimizer
from machine import SPI, Pin
import touch
from hw import LCD, IMU, TP

# --- Random ---
try:
    import urandom as random
except ImportError:
    import random

# ----------------------------
# 獨立的局部刷新函式 (取代 Monkey Patching)
# ----------------------------
def lcd_show_window(lcd, x, y, w, h):
    """
    只更新螢幕的特定矩形區域。
    參數:
        lcd: hw.LCD 物件
        x, y: 起始座標
        w, h: 寬度與高度
    """
    # 邊界檢查
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    
    if x < 0: x = 0
    if y < 0: y = 0
    if x + w > lcd.width: w = lcd.width - x
    if y + h > lcd.height: h = lcd.height - y
    if w <= 0 or h <= 0: return

    # 定義寫入指令的輔助函式 (直接操作 SPI，確保相容性)
    def write_cmd(cmd):
        lcd.cs(0)
        lcd.dc(0)
        lcd.spi.write(bytearray([cmd]))
        lcd.cs(1)

    def write_data(buf):
        lcd.cs(0)
        lcd.dc(1)
        lcd.spi.write(buf)
        lcd.cs(1)

    # 設定寫入視窗 (Column Address Set & Row Address Set)
    # 0x2A: Column Address Set
    write_cmd(0x2A)
    write_data(bytearray([x >> 8, x & 0xFF, (x + w - 1) >> 8, (x + w - 1) & 0xFF]))

    # 0x2B: Row Address Set
    write_cmd(0x2B)
    write_data(bytearray([y >> 8, y & 0xFF, (y + h - 1) >> 8, (y + h - 1) & 0xFF]))

    # 0x2C: Memory Write
    write_cmd(0x2C)

    # 開始傳送像素資料
    lcd.cs(0)
    lcd.dc(1)

    # 由於 framebuf 是線性的，我們需要針對每一行進行切片傳送
    buf = lcd.buffer
    stride = lcd.width * 2 # 每個像素 2 bytes
    
    # 建立 memoryview 以避免複製記憶體
    mv = memoryview(buf)
    
    if w == lcd.width:
        # 如果寬度剛好是全寬，可以一次傳送整塊，速度最快
        start_addr = y * stride
        end_addr = (y + h) * stride
        lcd.spi.write(mv[start_addr:end_addr])
    else:
        # 局部寬度，需要逐行傳送
        line_bytes = w * 2
        for i in range(h):
            start_addr = ((y + i) * stride) + (x * 2)
            lcd.spi.write(mv[start_addr : start_addr + line_bytes])

    lcd.cs(1)

# ----------------------------
# 遊戲參數與初始化
# ----------------------------

W, H = 240, 240
CX, CY = 120, 120
R_BOUND = 120

# 顏色定義
c_bg   = LCD.color(0, 0, 0)      # 黑色背景
c_ring = LCD.color(40, 40, 40)   # 迷宮外框
c_wall = LCD.color(80, 80, 255)  # 牆壁 (改亮一點比較好辨識)
c_ball = LCD.color(255, 255, 0)  # 黃色球

# 物理參數
ACC_SCALE = 2.5   # 加速度敏感度
DAMP = 0.95       # 阻尼 (摩擦力)
DEAD = 0.05       # IMU 死區
R_BALL = 6        # 球半徑

ball = {
    "x": CX, "y": CY,
    "vx": 0.0, "vy": 0.0,
    "r": R_BALL
}

WALLS = [] # 儲存牆壁資料: [x1, y1, x2, y2, thickness]

# ----------------------------
# 繪圖輔助函式
# ----------------------------

def draw_circle_ring(cx, cy, r, color):
    LCD.ellipse(cx, cy, r, r, color, False)

def draw_thick_line(x1, y1, x2, y2, thickness, color):
    # 簡單的粗線繪製，利用多條線偏移
    LCD.line(int(x1), int(y1), int(x2), int(y2), color)
    if thickness > 1:
        # 簡單的 X/Y 偏移模擬粗線 (效能考量)
        LCD.line(int(x1)+1, int(y1), int(x2)+1, int(y2), color)
        LCD.line(int(x1), int(y1)+1, int(x2), int(y2)+1, color)

def draw_ball(b, color):
    LCD.fill_rect(int(b["x"] - b["r"]), int(b["y"] - b["r"]), b["r"]*2, b["r"]*2, color)
    # 或者用圓形 (比較慢一點點，但好看)
    # LCD.ellipse(int(b["x"]), int(b["y"]), int(b["r"]), int(b["r"]), color, True)

# ----------------------------
# 迷宮生成邏輯 (Polar Maze)
# ----------------------------
def generate_polar_maze():
    global WALLS, ball
    LCD.fill(c_bg)
    LCD.text("Generating...", 70, 110, LCD.white)
    LCD.show()
    
    WALLS = []
    
    # 簡單的同心圓 + 缺口演算法
    rings = 4
    step = R_BOUND // (rings + 1)
    
    # 產生環狀牆壁 (Radial Walls)
    for i in range(1, rings + 1):
        r = i * step
        # 畫一圈，但在隨機位置留缺口
        gap_start = random.randint(0, 360)
        gap_size = 40 # 缺口角度大小
        
        # 為了簡化物理碰撞，我們將圓弧拆解成線段
        segs = 36 # 圓周解析度
        for s in range(segs):
            angle = s * (360 // segs)
            # 檢查是否在缺口內
            diff = abs(angle - gap_start)
            if diff > 180: diff = 360 - diff
            if diff < gap_size // 2:
                continue # 這是缺口
            
            # 計算線段起點與終點
            a1 = math.radians(angle)
            a2 = math.radians(angle + (360//segs))
            x1 = CX + r * math.cos(a1)
            y1 = CY + r * math.sin(a1)
            x2 = CX + r * math.cos(a2)
            y2 = CY + r * math.sin(a2)
            WALLS.append([x1, y1, x2, y2, 2]) # 厚度2

    # 重置球的位置到中心
    ball["x"], ball["y"] = CX, CY
    ball["vx"], ball["vy"] = 0, 0
    
    # 繪製完整的靜態背景一次
    LCD.fill(c_bg)
    draw_circle_ring(CX, CY, R_BOUND - 1, c_ring)
    for w in WALLS:
        draw_thick_line(w[0], w[1], w[2], w[3], w[4], c_wall)
    LCD.show()
    
    gc.collect()

# ----------------------------
# 物理與碰撞
# ----------------------------
def check_collision(new_x, new_y):
    # 1. 邊界檢查 (圓形邊界)
    dist_sq = (new_x - CX)**2 + (new_y - CY)**2
    if dist_sq > (R_BOUND - R_BALL)**2:
        return True # 撞到外牆

    # 2. 牆壁碰撞 (線段與球)
    # 為了效能，先做簡單的 Bounding Box 檢查
    bx1 = new_x - R_BALL
    bx2 = new_x + R_BALL
    by1 = new_y - R_BALL
    by2 = new_y + R_BALL

    for w in WALLS:
        wx1, wy1, wx2, wy2, th = w
        # 快速過濾: 如果牆壁的邊界框跟球沒接觸，直接跳過
        if max(wx1, wx2) < bx1 or min(wx1, wx2) > bx2: continue
        if max(wy1, wy2) < by1 or min(wy1, wy2) > by2: continue
        
        # 精確碰撞 (點到線段距離)
        # 線段向量
        dx = wx2 - wx1
        dy = wy2 - wy1
        if dx == 0 and dy == 0: continue
        
        # 投影
        t = ((new_x - wx1) * dx + (new_y - wy1) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t)) # 限制在線段內
        
        closest_x = wx1 + t * dx
        closest_y = wy1 + t * dy
        
        dist_w_sq = (new_x - closest_x)**2 + (new_y - closest_y)**2
        if dist_w_sq < (R_BALL + 1)**2: # +1 是容錯與牆壁厚度
            return True

    return False

# ----------------------------
# 主程式
# ----------------------------
def main():
    print("Starting Optimized Maze Game (No Types Mod)...")
    
    # 1. 生成初始迷宮
    generate_polar_maze()
    
    last_time = time.ticks_ms()
    updater = lcd_optimizer.ScreenUpdater(LCD)
    # 2. 主迴圈
    while True:
        # 計算時間差 (Delta Time) 以確保物理速度一致
        current_time = time.ticks_ms()
        dt_ms = time.ticks_diff(current_time, last_time)
        if dt_ms < 10: # 限制最高 FPS，避免運算過熱或過快
            continue
        last_time = current_time
        dt = dt_ms / 1000.0
        
        # --- 輸入處理 ---
        # 檢測觸控 (重置遊戲)
        if TP.Gestures == 0x01: # Slide Up or specific gesture
             pass
        try:
            TP.Get_Touch() # 更新觸控狀態
            if TP.Gestures == 0x0B or TP.Gestures == 0x05: # Double click or Single click
                generate_polar_maze()
                last_time = time.ticks_ms()
                continue
        except:
            pass # 忽略 I2C 錯誤

        # 讀取 IMU
        readings = IMU.Read_XYZ()
        if len(readings) >= 3:
            xg, yg, zg = readings[0], readings[1], readings[2]
        else:
            xg, yg, zg = 0, 0, 0

        # 計算傾斜 (簡單版)
        ax = yg * ACC_SCALE
        ay = -xg * ACC_SCALE
        
        # --- 物理積分 ---
        # 預測下一個位置
        next_vx = ball["vx"] + ax * dt * 50 # *50 是調整手感係數
        next_vy = ball["vy"] + ay * dt * 50
        
        next_vx *= DAMP
        next_vy *= DAMP
        
        next_x = ball["x"] + next_vx * dt * 50
        next_y = ball["y"] + next_vy * dt * 50
        
        # 碰撞檢測與反應
        if check_collision(next_x, next_y):
            # 簡單的反彈或停止
            ball["vx"] = -ball["vx"] * 0.3
            ball["vy"] = -ball["vy"] * 0.3
        else:
            ball["x"] = next_x
            ball["y"] = next_y
            ball["vx"] = next_vx
            ball["vy"] = next_vy

        # --- 繪圖 (關鍵優化部分) ---
        
        # 1. 計算髒矩形 (Dirty Rectangle)
        # 這是包含「舊球位置」與「新球位置」的最小矩形
        old_x, old_y = int(ball["x"] - ball["vx"]*dt*50), int(ball["y"] - ball["vy"]*dt*50) # 估算舊位置
        pad = R_BALL + 4
        
        min_x = int(min(ball["x"], old_x) - pad)
        max_x = int(max(ball["x"], old_x) + pad)
        min_y = int(min(ball["y"], old_y) - pad)
        max_y = int(max(ball["y"], old_y) + pad)
        
        # 邊界限制
        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(W, max_x)
        max_y = min(H, max_y)
        
        d_w = max_x - min_x
        d_h = max_y - min_y
        
        if d_w > 0 and d_h > 0:
            # 2. 清除髒矩形區域 (填入背景色)
            LCD.fill_rect(min_x, min_y, d_w, d_h, c_bg)
            
            # 3. 重繪髒矩形內的牆壁
            for w in WALLS:
                wx1, wy1, wx2, wy2, th = w
                # 檢查牆壁是否在髒矩形內
                if max(wx1, wx2) < min_x or min(wx1, wx2) > max_x: continue
                if max(wy1, wy2) < min_y or min(wy1, wy2) > max_y: continue
                
                # 如果在範圍內，重畫它
                draw_thick_line(wx1, wy1, wx2, wy2, th, c_wall)

            # 4. 畫新球
            draw_ball(ball, c_ball)
            
            # 5. 局部刷新到螢幕 (使用獨立函式呼叫)
            lcd_show_window(LCD, min_x, min_y, d_w, d_h)

if __name__ == '__main__':
    main()