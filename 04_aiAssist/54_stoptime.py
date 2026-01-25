import time
import math
from machine import RTC
import hw # 引入硬體定義

# ===== 顏色定義 (RGB565) =====
BLACK   = 0x0000
WHITE   = 0xFFFF
RED     = 0xF800
GREEN   = 0x07E0
BLUE    = 0x001F
CYAN    = 0x07FF
YELLOW  = 0xFFE0
ORANGE  = 0xFD20
DARKGRAY= 0x2104
LGRAY   = 0x8410  # 淺灰
NEON_GREEN = 0x07E0

# ===== 全域設定 =====
CENTER_X = 120
CENTER_Y = 120
STEP_GOAL = 10000

# 初始化 RTC
rtc = RTC()
# rtc.datetime((2024, 1, 1, 0, 12, 0, 0, 0)) 

# ==========================================
# 數學工具
# ==========================================
def deg_to_rad(degrees):
    return degrees * math.pi / 180

def get_coords(angle, radius, cx, cy):
    rad = deg_to_rad(angle)
    x = cx + int(radius * math.sin(rad))
    y = cy - int(radius * math.cos(rad))
    return x, y

# ==========================================
# 計步器邏輯 (輕量版)
# ==========================================
class StepCounter:
    def __init__(self, imu):
        self.imu = imu
        self.steps = 0
        self.threshold = 1.2
        self.last_mag = 0
        self.cooldown = 0
        
    def update(self):
        # 簡單讀取並偵測
        xyz = self.imu.Read_XYZ()
        mag = math.sqrt(xyz[0]**2 + xyz[1]**2 + xyz[2]**2)
        
        # 簡單的波峰判定
        if mag > self.threshold and self.last_mag <= self.threshold:
            if time.ticks_ms() > self.cooldown:
                self.steps += 1
                self.cooldown = time.ticks_ms() + 300 # 300ms 去抖動
        self.last_mag = mag
        return self.steps

# ==========================================
# 應用程式邏輯
# ==========================================
class SmartWatch:
    def __init__(self):
        self.mode = 'CLOCK' # CLOCK or STOPWATCH
        self.pedometer = StepCounter(hw.IMU)
        
        # 碼表變數
        self.sw_start_time = 0
        self.sw_elapsed = 0
        self.sw_running = False
        
        # 觸控變數
        self.last_touch_time = 0
        
    def check_touch(self):
        """偵測觸控並返回 (x, y) 或 None"""
        # 這裡假設 CST816T 驅動有更新 Touch 屬性
        # 根據 hw.py 的初始化，我們嘗試讀取 hw.TP
        try:
            # 不同的驅動版本讀取方式不同，這裡嘗試通用的屬性讀取
            # 如果您的 touch.py 有 scan() 方法，請在這裡呼叫
            # hw.TP.scan() 
            
            # 許多 CST816T micropython lib 會在有中斷時更新
            # 這裡我們模擬檢查 Gestures 或座標 (假設 hw.TP.Touch 存在或直接讀取暫存器)
            # 為了簡化，我們依賴 touch.py 內部的自動更新機制(如果有)
            # 若無，這裡可能需要根據您的 touch.py 實作做調整。
            
            # 假設: hw.TP.Gestures 非 0 代表有動作，或者 hw.TP.x_point 有值
            # 根據您提供的 touch.py snippet，它是事件驅動或輪詢
            # 這裡做一個簡單的輪詢假設
            
            # 注意：由於 touch.py 未完整提供，這裡假設 hw.TP 會有 x_point, y_point
            # 您可能需要檢查 hw.TP.read() 或類似函數
            
            # 模擬觸控讀取 (如果您的驅動不同，請修改此處)
            # 在這裡我們做一個防抖動
            if time.ticks_diff(time.ticks_ms(), self.last_touch_time) < 300:
                return None
                
            # 假設 hw.TP.Mode = 1 (Point mode)
            # 您可能需要呼叫 hw.TP.scan() 才能更新座標
            # 這裡暫時假設 hw.TP 對象有些屬性可以讀
            # 如果無法讀取，請嘗試 hw.TP.Get_Point()
            
            # 為了避免報錯，我們用 try-except 包裹實際讀取邏輯
            # 如果您的 touch.py 會自動 print 座標，那需要改寫 touch.py 才能獲取
            pass 
            
            # 實際整合時，請查看 touch.py 的 def Get_Point(self):
            # 這裡假設一個介面:
            # gesture = hw.TP.Gestures
            # x = hw.TP.x_point
            # y = hw.TP.y_point
            # if gesture != 0: ...
            
        except:
            pass
        return None

    def draw_tech_circle(self, cx, cy, r, color, thickness=1):
        """繪製科技感的圓框 (帶缺口)"""
        # 畫四段弧線模擬儀表框
        for i in range(0, 360, 90):
            # 每個象限畫一段
            for ang in range(i+10, i+80, 5): # 留空隙
                x1, y1 = get_coords(ang, r, cx, cy)
                hw.LCD.pixel(x1, y1, color)
                if thickness > 1:
                    x2, y2 = get_coords(ang, r-1, cx, cy)
                    hw.LCD.pixel(x2, y2, color)

    def draw_hand_tri(self, cx, cy, angle, length, width, color):
        """繪製三角形指針"""
        rad = deg_to_rad(angle)
        x_tip = cx + int(length * math.sin(rad))
        y_tip = cy - int(length * math.cos(rad))
        
        # 尾部與兩側
        tail_len = 5
        x_tail = cx - int(tail_len * math.sin(rad))
        y_tail = cy + int(tail_len * math.cos(rad))
        
        x_l = cx + int(width * math.sin(rad - 1.57))
        y_l = cy - int(width * math.cos(rad - 1.57))
        x_r = cx + int(width * math.sin(rad + 1.57))
        y_r = cy - int(width * math.cos(rad + 1.57))
        
        hw.LCD.fill_tri(x_l, y_l, x_r, y_r, x_tip, y_tip, color)
        # 畫個中心點
        hw.LCD.fill_rect(cx-2, cy-2, 4, 4, WHITE)

    def draw_clock_face(self, dt, steps):
        # 清屏
        hw.LCD.fill(BLACK)
        
        # 1. 繪製佈局框架 (科技感線條)
        # 連接線
        hw.LCD.line(120, 70, 60, 160, DARKGRAY)
        hw.LCD.line(120, 70, 180, 160, DARKGRAY)
        hw.LCD.line(60, 160, 180, 160, DARKGRAY)
        
        # ============================
        # 上方主環：分針 (Minute) - 黃色
        # ============================
        mcx, mcy = 120, 70
        mr = 45
        self.draw_tech_circle(mcx, mcy, mr, YELLOW, 2)
        hw.LCD.write_text("MIN", mcx-12, mcy-25, 1, YELLOW)
        # 分針
        min_ang = dt[5] * 6
        self.draw_hand_tri(mcx, mcy, min_ang, 40, 4, YELLOW)
        
        # ============================
        # 左下環：時針 (Hour) - 青色
        # ============================
        hcx, hcy = 60, 160
        hr = 35
        self.draw_tech_circle(hcx, hcy, hr, CYAN, 2)
        hw.LCD.write_text("HOUR", hcx-16, hcy+15, 1, CYAN)
        # 時針
        hour_ang = (dt[4] % 12) * 30 + dt[5]*0.5
        self.draw_hand_tri(hcx, hcy, hour_ang, 30, 3, CYAN)

        # ============================
        # 右下環：秒針 (Second) - 橙紅色
        # ============================
        scx, scy = 180, 160
        sr = 35
        self.draw_tech_circle(scx, scy, sr, ORANGE, 2)
        hw.LCD.write_text("SEC", scx-12, scy+15, 1, ORANGE)
        # 秒針
        sec_ang = dt[6] * 6
        self.draw_hand_tri(scx, scy, sec_ang, 30, 2, RED)

        # ============================
        # 中央資訊區
        # ============================
        # 數位時間 (大)
        time_str = "{:02d}:{:02d}".format(dt[4], dt[5])
        # 陰影效果
        hw.LCD.write_text(time_str, 82, 112, 2, DARKGRAY) 
        hw.LCD.write_text(time_str, 80, 110, 2, WHITE)
        
        # 日期 (上方)
        date_str = "{:02d}-{:02d}".format(dt[1], dt[2])
        hw.LCD.write_text(date_str, 100, 20, 1, LGRAY)

        # ============================
        # 右側計步條 (弧形)
        # ============================
        # 在最右側畫一條垂直能量條
        pct = min(steps / STEP_GOAL, 1.0)
        bar_height = 80
        fill_h = int(bar_height * pct)
        hw.LCD.rect(225, 80, 6, 80, DARKGRAY)
        hw.LCD.fill_rect(226, 80 + (80-fill_h), 4, fill_h, NEON_GREEN)
        hw.LCD.write_text("S", 225, 65, 1, NEON_GREEN) # S for Steps
        
        # 觸控提示點 (底部中央)
        hw.LCD.fill_rect(115, 220, 10, 10, WHITE)
        hw.LCD.write_text("TAP", 108, 232, 1, LGRAY)

    def draw_stopwatch_face(self):
        hw.LCD.fill(BLACK)
        
        # 標題
        hw.LCD.write_text("CHRONO", 95, 20, 1, CYAN)
        
        # 計算時間
        total_ms = self.sw_elapsed
        if self.sw_running:
            total_ms += time.ticks_diff(time.ticks_ms(), self.sw_start_time)
            
        seconds = (total_ms // 1000) % 60
        minutes = (total_ms // 60000) % 60
        millis = (total_ms % 1000) // 10
        
        # 顯示大時間 MM:SS
        main_str = "{:02d}:{:02d}".format(minutes, seconds)
        hw.LCD.write_text(main_str, 50, 80, 4, WHITE)
        
        # 顯示毫秒 (下方)
        ms_str = ".{:02d}".format(millis)
        hw.LCD.write_text(ms_str, 160, 115, 2, YELLOW)
        
        # 繪製動態圈 (秒數進度)
        sec_prog = seconds / 60.0
        # 畫一個簡單的進度條在上方
        bar_w = 200
        hw.LCD.rect(20, 60, bar_w, 6, DARKGRAY)
        hw.LCD.fill_rect(20, 60, int(bar_w * sec_prog), 6, ORANGE)
        
        # 按鈕 UI 指示
        # 上半部: START/STOP
        # 下半部: RESET/EXIT
        status_color = GREEN if self.sw_running else RED
        status_text = "RUN" if self.sw_running else "PAUSE"
        
        hw.LCD.fill_rect(0, 140, 240, 2, DARKGRAY) # 分隔線
        
        # Start/Stop 區域
        hw.LCD.write_text(status_text, 90, 160, 2, status_color)
        
        # Reset/Exit 區域
        hw.LCD.write_text("RESET/EXIT", 80, 200, 1, LGRAY)

    def run(self):
        print("Watch System Started")
        while True:
            # 1. 更新感測器
            steps = self.pedometer.update()
            
            # 2. 處理觸控 (模擬)
            # 由於我們沒有完整的 touch.py 文件，這裡使用一個簡化的假設：
            # 我們假設若有觸摸，我們能讀取到某些標誌。
            # 這裡我們模擬：如果 I2C 讀取到觸控中斷 (通常 Pin 17 or similar)
            # 為了演示，我們使用一個「假想」的 Get_Point 封裝
            # 實務上您需要呼叫 hw.TP.Get_Point() 或是讀取 hw.TP.Gestures
            
            # --- 模擬觸控偵測區域 ---
            # 請依照您的 touch.py 實際情況修改這裡
            # 範例：如果 hw.TP.Gestures 變更
            try:
                # 嘗試讀取硬體
                # hw.TP.scan() # 若 library 需要手動掃描
                pass
            except:
                pass
                
            # 這裡為了能夠執行，我們預設不觸發，
            # 若您實際按壓，請確保 touch.py 能正確寫入 hw.TP.x/y
            # 假設有觸控:
            touched = False
            t_x, t_y = 0, 0
            
            # *** 這裡請根據您的硬體修改 ***
            # if hw.TP.Gestures: ...
            
            # 為了演示模式切換，我們寫死一個邏輯：
            # 如果是模擬環境或您需要測試，可以用特定的感測器動作代替觸控
            # 例如：用力甩動手錶 (加速度 > 3g) 切換模式 (作為備案)
            xyz = hw.IMU.Read_XYZ()
            acc_mag = math.sqrt(xyz[0]**2 + xyz[1]**2 + xyz[2]**2)
            shake_trigger = acc_mag > 3.0 # 用力甩動切換
            
            # 3. 狀態機與繪圖
            if self.mode == 'CLOCK':
                # 繪製時鐘
                dt = rtc.datetime()
                self.draw_clock_face(dt, steps)
                
                # 檢查切換條件 (觸控或甩動)
                # 如果觸控點在底部 (y > 200) -> 進入碼表
                # 這裡暫時用甩動代替觸控 demo，或者您可以將變數改為真實觸控
                if shake_trigger: 
                    self.mode = 'STOPWATCH'
                    self.sw_running = False
                    self.sw_elapsed = 0
                    time.sleep(0.5) # 防抖
            
            elif self.mode == 'STOPWATCH':
                self.draw_stopwatch_face()
                
                # 操作邏輯 (模擬)
                # 點擊上半部 -> Start/Pause
                # 點擊下半部 -> Reset (若暫停) 或 Exit (若 Reset 後)
                
                if shake_trigger: # 用甩動模擬按鈕 (真實情況請用 touch x,y 判斷)
                    if not self.sw_running:
                        # Start
                        self.sw_running = True
                        self.sw_start_time = time.ticks_ms()
                    else:
                        # Pause
                        self.sw_running = False
                        self.sw_elapsed += time.ticks_diff(time.ticks_ms(), self.sw_start_time)
                    time.sleep(0.5)
                
                # 長按或特定區域退出 (這裡簡化為：若暫停太久自動退出)
                if not self.sw_running and self.sw_elapsed > 0 and acc_mag > 4.0: # 極用力甩退出
                     self.mode = 'CLOCK'
                     time.sleep(0.5)

            hw.LCD.show()
            # 稍微延遲避免過熱，碼表模式下要快一點
            delay = 0.05 if self.mode == 'STOPWATCH' and self.sw_running else 0.1
            time.sleep(delay)

if __name__ == '__main__':
    app = SmartWatch()
    app.run()