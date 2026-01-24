# lcd_optimizer.py
# 專門用於加速 Waveshare 1.28 LCD 的局部刷新工具
import math

class ScreenUpdater:
    def __init__(self, lcd):
        self.lcd = lcd
        self.last_x = None
        self.last_y = None
        self.width = lcd.width
        self.height = lcd.height

    def refresh(self, x, y, r, padding=4):
        """
        只更新球移動前後的區域 (Dirty Rectangle)。
        x, y: 球的新座標
        r: 球的半徑
        padding: 額外擴展範圍，防止殘影
        """
        x = int(x)
        y = int(y)
        r = int(r)
        
        # 如果是第一次執行，記錄位置但不刷新 (或全屏刷新)
        if self.last_x is None:
            self.last_x = x
            self.last_y = y
            self.lcd.show() # 第一次仍需全屏
            return

        # 計算「舊位置」與「新位置」的聯集矩形
        min_x = min(x, self.last_x) - r - padding
        max_x = max(x, self.last_x) + r + padding
        min_y = min(y, self.last_y) - r - padding
        max_y = max(y, self.last_y) + r + padding

        # 邊界限制
        if min_x < 0: min_x = 0
        if min_y < 0: min_y = 0
        if max_x > self.width: max_x = self.width
        if max_y > self.height: max_y = self.height

        w = max_x - min_x
        h = max_y - min_y

        if w > 0 and h > 0:
            self._show_window(min_x, min_y, w, h)
        
        # 更新舊位置
        self.last_x = x
        self.last_y = y

    def _show_window(self, x, y, w, h):
        """直接操作 SPI 進行局部更新"""
        # 設置寫入視窗 (Column / Row Address Set)
        # 這些指令適用於 GC9A01 和 ST7789
        self.lcd.cs(0)
        
        # CASET (2Ah)
        self.lcd.dc(0)
        self.lcd.spi.write(b'\x2A')
        self.lcd.dc(1)
        self.lcd.spi.write(bytearray([x >> 8, x & 0xFF, (x + w - 1) >> 8, (x + w - 1) & 0xFF]))
        
        # RASET (2Bh)
        self.lcd.dc(0)
        self.lcd.spi.write(b'\x2B')
        self.lcd.dc(1)
        self.lcd.spi.write(bytearray([y >> 8, y & 0xFF, (y + h - 1) >> 8, (y + h - 1) & 0xFF]))
        
        # RAMWR (2Ch)
        self.lcd.dc(0)
        self.lcd.spi.write(b'\x2C')
        self.lcd.dc(1)
        
        # 傳送像素資料
        # 為了效能，這裡直接切片 memoryview
        buf = self.lcd.buffer
        stride = self.width * 2
        mv = memoryview(buf)
        
        # 如果寬度是全螢幕寬，可以一次傳送整塊
        if w == self.width:
            start_addr = y * stride
            end_addr = (y + h) * stride
            self.lcd.spi.write(mv[start_addr:end_addr])
        else:
            # 否則需要逐行傳送
            line_bytes = w * 2
            for i in range(h):
                start_addr = ((y + i) * stride) + (x * 2)
                self.lcd.spi.write(mv[start_addr : start_addr + line_bytes])
        
        self.lcd.cs(1)