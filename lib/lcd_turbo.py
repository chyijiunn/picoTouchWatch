# lcd_turbo.py
# 極速版局部刷新驅動，針對 RP2040 優化
# 使用預先分配的緩衝區與單次 SPI 傳輸，減少通訊延遲

import machine

class TurboUpdater:
    def __init__(self, lcd, max_size=60):
        self.lcd = lcd
        self.last_x = None
        self.last_y = None
        self.width = lcd.width
        self.height = lcd.height
        
        # 預先分配一個足夠大的緩衝區 (Scratch Buffer)
        # 假設最大更新區塊為 max_size x max_size (例如 60x60)
        # 每個像素 2 bytes
        self.max_size = max_size
        self.scratch = bytearray(max_size * max_size * 2)
        
        # 取得 LCD 緩衝區的記憶體視圖 (MemoryView)，加速存取
        self.src_mv = memoryview(lcd.buffer)
        self.stride = lcd.width * 2
        
    def refresh(self, x, y, r, padding=4):
        """
        極速刷新：計算範圍 -> 打包像素 -> 單次傳送
        """
        x = int(x)
        y = int(y)
        r = int(r)
        
        # 第一次執行全屏刷新
        if self.last_x is None:
            self.last_x = x
            self.last_y = y
            self.lcd.show()
            return

        # 計算髒矩形 (Dirty Rectangle)
        min_x = min(x, self.last_x) - r - padding
        max_x = max(x, self.last_x) + r + padding
        min_y = min(y, self.last_y) - r - padding
        max_y = max(y, self.last_y) + r + padding

        # 邊界限制
        if min_x < 0: min_x = 0
        if min_y < 0: min_y = 0
        if max_x > self.width: max_x = self.width
        if max_y > self.height: max_y = self.height

        w = int(max_x - min_x)
        h = int(max_y - min_y)

        # 如果沒有移動或範圍無效，跳過
        if w <= 0 or h <= 0:
            return

        # 如果更新範圍超過緩衝區大小，限制它 (安全機制)
        # 雖然這可能導致畫面邊緣殘影，但能防止崩潰
        if w > self.max_size: w = self.max_size
        if h > self.max_size: h = self.max_size

        # 執行快速傳送
        self._blit_fast(min_x, min_y, w, h)
        
        # 更新舊位置
        self.last_x = x
        self.last_y = y

    def _blit_fast(self, x, y, w, h):
        """
        將主緩衝區的不連續資料複製到連續的 scratch 緩衝區，然後一次發送
        """
        # 準備 SPI 指令
        self.lcd.cs(0)
        
        # 1. 設定視窗 (Window)
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
        
        # 2. 數據打包 (Data Packing)
        # 利用 slice assignment 進行快速記憶體複製
        # 這是 MicroPython 中最快的純 Python 複製方式
        src_stride = self.stride
        dst_width_bytes = w * 2
        
        # 針對每一行，將資料搬移到 scratch buffer
        # 雖然這裡有 Python 迴圈，但因為操作的是 memoryview，速度尚可
        # 且 SPI 寫入只有最後一次，大幅減少硬體交握時間
        idx = 0
        for r in range(h):
            start = (y + r) * src_stride + (x * 2)
            # 複製一行
            self.scratch[idx : idx + dst_width_bytes] = self.src_mv[start : start + dst_width_bytes]
            idx += dst_width_bytes
            
        # 3. 單次傳送 (Single Shot Transfer)
        # 只傳送有效數據部分
        self.lcd.spi.write(self.scratch[:idx])
        
        self.lcd.cs(1)