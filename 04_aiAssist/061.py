import time
import math
from machine import RTC
import hw # 引入您提供的 hw.py (已經包含了 touch.py 的初始化)

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

# ===== 設定中心點與半徑 =====
CENTER_X = 120
CENTER_Y = 120
RADIUS   = 120

# 初始化 RTC (如果沒有網路校時，每次重啟會重置)
# 格式: (year, month, day, weekday, hour, minute, second, subseconds)
rtc = RTC()
# 為了演示，如果您需要設定時間，請取消下面這行的註解並修改數值：
# rtc.datetime((2024, 5, 20, 0, 10, 30, 0, 0)) 

def deg_to_rad(degrees):
    """將角度轉換為弧度"""
    return degrees * math.pi / 180

def get_circle_coords(angle_deg, radius, cx=CENTER_X, cy=CENTER_Y):
    """
    根據角度和半徑獲取座標
    0度/360度 對應 12點鐘方向
    """
    # 調整角度，使 0 度指向 12 點鐘 (數學上 0 度通常是 3 點鐘)
    # x = cx + r * sin(a)
    # y = cy - r * cos(a)
    rad = deg_to_rad(angle_deg)
    x = cx + int(radius * math.sin(rad))
    y = cy - int(radius * math.cos(rad))
    return x, y

def draw_face():
    """繪製錶盤刻度"""
    # 繪製 60 個刻度
    for i in range(60):
        # 外圈半徑與內圈半徑
        r_outer = 118
        if i % 5 == 0:
            # 整點刻度 (大)
            r_inner = 105
            color = WHITE
            # 繪製加粗的刻度 (畫兩次稍微偏移)
            x1, y1 = get_circle_coords(i * 6, r_outer)
            x2, y2 = get_circle_coords(i * 6, r_inner)
            hw.LCD.line(x1, y1, x2, y2, color)
            hw.LCD.line(x1+1, y1, x2+1, y2, color)
        else:
            # 分鐘刻度 (小)
            r_inner = 114
            color = GRAY
            x1, y1 = get_circle_coords(i * 6, r_outer)
            x2, y2 = get_circle_coords(i * 6, r_inner)
            hw.LCD.line(x1, y1, x2, y2, color)

    # 繪製 12, 3, 6, 9 的數字或裝飾 (這裡用小矩形裝飾)
    hw.LCD.fill_rect(CENTER_X-2, 0, 4, 10, ORANGE)   # 12點
    hw.LCD.fill_rect(CENTER_X-2, 230, 4, 10, WHITE)  # 6點
    hw.LCD.fill_rect(0, CENTER_Y-2, 10, 4, WHITE)    # 9點
    hw.LCD.fill_rect(230, CENTER_Y-2, 10, 4, WHITE)  # 3點

def draw_fancy_hand(angle, length, width, color, tail_length=0):
    """
    繪製漂亮的劍形指針 (使用三角形填充)
    angle: 指向的角度 (0-360)
    length: 指針長度
    width: 指針底座寬度的一半
    color: 顏色
    tail_length: 尾部超出的長度
    """
    rad = deg_to_rad(angle)
    
    # 指針尖端
    x_tip = CENTER_X + int(length * math.sin(rad))
    y_tip = CENTER_Y - int(length * math.cos(rad))
    
    # 指針尾端 (為了平衡感)
    x_tail = CENTER_X - int(tail_length * math.sin(rad))
    y_tail = CENTER_Y + int(tail_length * math.cos(rad))
    
    # 計算左右兩側的點 (垂直於指針方向)
    # 左側點角度 = 指針角度 - 90度
    x_left = CENTER_X + int(width * math.sin(rad - math.pi/2))
    y_left = CENTER_Y - int(width * math.cos(rad - math.pi/2))
    
    # 右側點角度 = 指針角度 + 90度
    x_right = CENTER_X + int(width * math.sin(rad + math.pi/2))
    y_right = CENTER_Y - int(width * math.cos(rad + math.pi/2))
    
    # 繪製主體 (底座到尖端)
    hw.LCD.fill_tri(x_left, y_left, x_right, y_right, x_tip, y_tip, color)
    
    # 繪製尾部 (如果有)
    if tail_length > 0:
        hw.LCD.fill_tri(x_left, y_left, x_right, y_right, x_tail, y_tail, color)

def display_digital_info(dt):
    """顯示數位時間和日期"""
    # dt 格式: (year, month, day, weekday, hour, minute, second, subseconds)
    
    # 格式化日期字串 YYYY-MM-DD
    date_str = "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])
    
    # 格式化時間字串 HH:MM
    time_str = "{:02d}:{:02d}".format(dt[4], dt[5])
    
    # 計算文字寬度以置中 (假設字體寬度固定，這裡做簡單估算)
    # write_text(text, x, y, size, color)
    
    # 顯示日期 (上方)
    hw.LCD.write_text(date_str, 65, 60, 1, CYAN)
    
    # 顯示數位時間 (下方)
    hw.LCD.write_text(time_str, 80, 160, 2, WHITE)

def main():
    print("Watch Face Started...")
    
    while True:
        # 1. 獲取當前時間
        dt = rtc.datetime()
        hour = dt[4]
        minute = dt[5]
        second = dt[6]
        
        # 2. 清空緩衝區 (填入黑色背景)
        hw.LCD.fill(BLACK)
        
        # 3. 繪製靜態錶盤
        draw_face()
        
        # 4. 繪製數位資訊
        display_digital_info(dt)
        
        # 5. 計算指針角度
        # 秒針: 360 / 60 = 6度/秒
        sec_angle = second * 6 
        
        # 分針: 6度/分 + (秒/60 * 6) 讓分針隨秒平滑移動
        min_angle = minute * 6 + (second * 0.1)
        
        # 時針: 360 / 12 = 30度/小時 + (分/60 * 30)
        hour_angle = (hour % 12) * 30 + (minute * 0.5)
        
        # 6. 繪製指針 (順序：時 -> 分 -> 秒，這樣秒針會疊在最上面)
        
        # 時針 (短、粗、青色)
        draw_fancy_hand(hour_angle, length=55, width=6, color=CYAN, tail_length=10)
        
        # 分針 (長、中等、黃色)
        draw_fancy_hand(min_angle, length=85, width=4, color=YELLOW, tail_length=15)
        
        # 秒針 (最長、細、橙色，帶明顯尾巴)
        # 為了讓秒針更明顯，我們先畫一條線，再畫裝飾
        s_x, s_y = get_circle_coords(sec_angle, 95)
        s_tx, s_ty = get_circle_coords(sec_angle + 180, 20) # 尾部
        hw.LCD.line(s_tx, s_ty, s_x, s_y, ORANGE)
        # 秒針中心的裝飾圓點 (用小矩形模擬)
        hw.LCD.fill_rect(CENTER_X-2, CENTER_Y-2, 4, 4, RED)
        # 秒針尖端的裝飾
        draw_fancy_hand(sec_angle, length=95, width=2, color=ORANGE, tail_length=20)

        # 7. 繪製中心蓋板 (遮住指針交匯處的雜亂)
        hw.LCD.fill_rect(CENTER_X-3, CENTER_Y-3, 6, 6, WHITE)
        
        # 8. 更新螢幕
        hw.LCD.show()
        
        # 9. 延時 (稍微小於1秒以保持流暢，或使用0.1秒提高分針流暢度)
        time.sleep(0.2)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # 按 Ctrl+C 停止時清空螢幕
        hw.LCD.fill(0)
        hw.LCD.show()