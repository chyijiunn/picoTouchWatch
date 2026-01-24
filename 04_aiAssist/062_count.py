import time
import math
from machine import RTC
import hw # 引入 hw.py (包含 touch.py 的初始化)

# ===== 顏色定義 (RGB565) =====
BLACK   = 0x0000
WHITE   = 0xFFFF
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
CYAN    = 0x07FF
YELLOW  = 0xFFE0
ORANGE  = 0xFD20
GRAY    = 0x8410
DARKGRAY= 0x4208
LIME    = 0x07E0 # 鮮綠色用於計步圈

# ===== 設定中心點與半徑 =====
CENTER_X = 120
CENTER_Y = 120
RADIUS   = 120

# ===== 計步器目標 =====
STEP_GOAL = 100

# 初始化 RTC
rtc = RTC()
# rtc.datetime((2024, 1, 1, 0, 10, 0, 0, 0)) # 若需校時請取消註解

# ==========================================
# 工具函式
# ==========================================
def deg_to_rad(degrees):
    return degrees * math.pi / 180

def get_circle_coords(angle_deg, radius, cx=CENTER_X, cy=CENTER_Y):
    rad = deg_to_rad(angle_deg)
    x = cx + int(radius * math.sin(rad))
    y = cy - int(radius * math.cos(rad))
    return x, y

# ==========================================
# 計步器類別
# ==========================================
class StepCounter:
    def __init__(self, imu, threshold=1.15, debounce_ms=300):
        self.imu = imu
        self.steps = 0
        self.threshold = threshold      # 加速度閾值 (g)
        self.debounce_ms = debounce_ms  # 最小步頻間隔 (毫秒)
        self.last_step_time = 0
        self.state = 0 # 0: 等待波峰, 1: 等待波谷
        
    def update(self):
        # 讀取 IMU 數據 (x, y, z, gx, gy, gz)
        # 根據 QMI8658 驅動，返回值單位約為 1g = 1.0
        xyz = self.imu.Read_XYZ()
        ax, ay, az = xyz[0], xyz[1], xyz[2]
        
        # 計算合加速度向量長度
        magnitude = math.sqrt(ax*ax + ay*ay + az*az)
        
        current_time = time.ticks_ms()
        
        # 簡單的波峰偵測演算法
        # 狀態 0: 等待加速度大於閾值 (腳落地衝擊)
        if self.state == 0:
            if magnitude > self.threshold:
                self.state = 1
        
        # 狀態 1: 確認是否為有效步數 (過濾雜訊並檢查時間間隔)
        elif self.state == 1:
            # 當加速度回落到 1g 以下 (或接近 1g)，且距離上一步夠久
            if magnitude < 1.05: 
                if time.ticks_diff(current_time, self.last_step_time) > self.debounce_ms:
                    self.steps += 1
                    self.last_step_time = current_time
                    # print(f"Steps: {self.steps}")
                self.state = 0
                
        return self.steps

# 初始化計步器
pedometer = StepCounter(hw.IMU)

# ==========================================
# 繪圖函式
# ==========================================
def draw_face():
    """繪製錶盤刻度"""
    for i in range(60):
        r_outer = 118
        if i % 5 == 0:
            r_inner = 105
            color = WHITE
            x1, y1 = get_circle_coords(i * 6, r_outer)
            x2, y2 = get_circle_coords(i * 6, r_inner)
            hw.LCD.line(x1, y1, x2, y2, color)
            hw.LCD.line(x1+1, y1, x2+1, y2, color)
        else:
            r_inner = 114
            color = GRAY
            x1, y1 = get_circle_coords(i * 6, r_outer)
            x2, y2 = get_circle_coords(i * 6, r_inner)
            hw.LCD.line(x1, y1, x2, y2, color)

    # 裝飾點
    hw.LCD.fill_rect(CENTER_X-2, 0, 4, 10, ORANGE)
    hw.LCD.fill_rect(CENTER_X-2, 230, 4, 10, WHITE)
    hw.LCD.fill_rect(0, CENTER_Y-2, 10, 4, WHITE)
    # 右邊刻度因為要放計步圈，可以稍微縮短或省略
    # hw.LCD.fill_rect(230, CENTER_Y-2, 10, 4, WHITE) 

def draw_fancy_hand(angle, length, width, color, tail_length=0):
    """繪製指針"""
    rad = deg_to_rad(angle)
    x_tip = CENTER_X + int(length * math.sin(rad))
    y_tip = CENTER_Y - int(length * math.cos(rad))
    x_tail = CENTER_X - int(tail_length * math.sin(rad))
    y_tail = CENTER_Y + int(tail_length * math.cos(rad))
    
    # 左右寬度擴展
    x_left = CENTER_X + int(width * math.sin(rad - math.pi/2))
    y_left = CENTER_Y - int(width * math.cos(rad - math.pi/2))
    x_right = CENTER_X + int(width * math.sin(rad + math.pi/2))
    y_right = CENTER_Y - int(width * math.cos(rad + math.pi/2))
    
    hw.LCD.fill_tri(x_left, y_left, x_right, y_right, x_tip, y_tip, color)
    if tail_length > 0:
        hw.LCD.fill_tri(x_left, y_left, x_right, y_right, x_tail, y_tail, color)

def draw_step_ring(steps, goal):
    """
    在右側繪製環狀計步顯示
    """
    # 圓圈設定
    ring_cx = 185 # 圓心 X (靠右)
    ring_cy = 120 # 圓心 Y (垂直置中)
    ring_r  = 22  # 半徑
    
    # 計算百分比 (最高 100%)
    percentage = min(steps / goal, 1.0)
    
    # 繪製底環 (深灰色) - 用點畫圓比較慢，這裡用畫多邊形或粗略點模擬
    # 為了效能，我們畫一個較粗的圓環 (透過畫多個同心圓或數學計算)
    # 這裡採用簡單的點繪製法，每隔幾度畫一個點
    for angle in range(0, 360, 10): 
        # 畫底色環
        rx = ring_cx + int(ring_r * math.sin(deg_to_rad(angle)))
        ry = ring_cy - int(ring_r * math.cos(deg_to_rad(angle)))
        hw.LCD.pixel(rx, ry, DARKGRAY)
        # 稍微加粗
        rx2 = ring_cx + int((ring_r-1) * math.sin(deg_to_rad(angle)))
        ry2 = ring_cy - int((ring_r-1) * math.cos(deg_to_rad(angle)))
        hw.LCD.pixel(rx2, ry2, DARKGRAY)

    # 繪製進度環 (亮色)
    end_angle = int(percentage * 360)
    for angle in range(0, end_angle, 5): # 步進 5 度比較密
        # 內外畫兩層像素以加粗線條
        rx = ring_cx + int(ring_r * math.sin(deg_to_rad(angle)))
        ry = ring_cy - int(ring_r * math.cos(deg_to_rad(angle)))
        hw.LCD.pixel(rx, ry, LIME)
        
        rx2 = ring_cx + int((ring_r-1) * math.sin(deg_to_rad(angle)))
        ry2 = ring_cy - int((ring_r-1) * math.cos(deg_to_rad(angle)))
        hw.LCD.pixel(rx2, ry2, LIME)
        
    # 顯示百分比文字
    pct_text = "{:d}%".format(int(percentage * 100))
    # 文字置中修正 (大概估算)
    text_x = ring_cx - (len(pct_text) * 4) 
    hw.LCD.write_text(pct_text, text_x, ring_cy - 4, 1, WHITE)
    
    # 在環下方顯示圖示或小標題
    hw.LCD.write_text("STEPS", ring_cx - 15, ring_cy + 25, 1, GRAY)

def main():
    print("Watch Face with Pedometer Started...")
    
    # 為了讓計步更準確，主迴圈速度不能太慢
    # 但為了讓動畫流暢，也不能完全被繪圖卡住
    # 這裡採用計步優先，繪圖定時更新的策略
    
    last_draw_time = 0
    draw_interval = 100 # 每 100ms 更新一次畫面 (10FPS)，保留時間給計步偵測
    
    while True:
        # 1. 更新計步器 (必須高頻率呼叫)
        current_steps = pedometer.update()
        
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_draw_time) < draw_interval:
            # 還沒到畫圖時間，稍微休息一下讓 CPU 處理其他中斷，繼續偵測步數
            time.sleep(0.01) 
            continue
            
        last_draw_time = current_time
        
        # 2. 準備繪圖
        dt = rtc.datetime()
        hw.LCD.fill(BLACK)
        
        # 3. 繪製錶盤與資訊
        draw_face()
        
        # 顯示日期 (左移一點避開右邊的圈圈)
        date_str = "{:02d}-{:02d}".format(dt[1], dt[2]) # MM-DD
        hw.LCD.write_text(date_str, 50, 60, 1, CYAN)
        
        # 顯示數位時間
        time_str = "{:02d}:{:02d}".format(dt[4], dt[5])
        hw.LCD.write_text(time_str, 80, 160, 2, WHITE)
        
        # 4. 繪製計步器圓環 (新增功能)
        draw_step_ring(current_steps, STEP_GOAL)
        
        # 5. 繪製指針
        second = dt[6]
        minute = dt[5]
        hour = dt[4]
        
        sec_angle = second * 6
        min_angle = minute * 6 + (second * 0.1)
        hour_angle = (hour % 12) * 30 + (minute * 0.5)
        
        draw_fancy_hand(hour_angle, 55, 6, CYAN, 10)
        draw_fancy_hand(min_angle, 85, 4, YELLOW, 15)
        
        # 秒針
        s_x, s_y = get_circle_coords(sec_angle, 95)
        s_tx, s_ty = get_circle_coords(sec_angle + 180, 20)
        hw.LCD.line(s_tx, s_ty, s_x, s_y, ORANGE)
        hw.LCD.fill_rect(CENTER_X-2, CENTER_Y-2, 4, 4, RED)
        draw_fancy_hand(sec_angle, 95, 2, ORANGE, 20)
        
        # 中心蓋板
        hw.LCD.fill_rect(CENTER_X-3, CENTER_Y-3, 6, 6, WHITE)
        
        hw.LCD.show()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass