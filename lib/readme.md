# RP2040 圓形螢幕 Launcher / Menu 專案說明

本專案為基於 **RP2040 + 1.28" 240×240 圓形 LCD（RGB565）** 的 MicroPython 系統，  
提供一個 **圓形表盤式 Launcher / Menu**，可透過觸控滑動與點選執行裝置內的 `.py` 腳本。

專案重點在於：
- 避免重複配置 FrameBuffer（115200 bytes）造成 MemoryError
- 統一硬體初始化（LCD / Touch / IMU）
- 讓「被 Menu 執行的腳本」與「單獨執行的腳本」都能安全運作

---

## 專案目錄結構

```
/
├─ main.py              # 系統進入點，只負責啟動 menu
└─ lib/
   ├─ touch.py          # 底層硬體 driver（LCD / Touch / IMU）
   ├─ hw.py (可選)      # 硬體單例層（LCD / IMU / Touch 只建立一次）
   └─ menu.py           # 圓形表盤 Launcher / Menu
```

---

## /lib/touch.py — 底層硬體 Driver

### 功能
`touch.py` 為硬體驅動層（driver layer），負責提供：

- LCD_1inch28  
  - 240×240 RGB565 LCD FrameBuffer  
  - SPI 傳輸、`LCD.show()` 顯示更新
- Touch_CST816T  
  - 電容式觸控 IC（CST816T）  
  - 使用中斷（IRQ）更新 X_point / Y_point / Flag
- QMI8658  
  - 六軸 IMU（加速度 / 陀螺儀）

### 設計原則
- 僅提供 class / function，不主動建立大型物件
- 避免在 `import touch` 時直接配置 115200 bytes FrameBuffer
- 若整合硬體單例，必須使用懶初始化（lazy init）

---

## /lib/hw.py（可選）— 硬體單例層（Hardware Singletons）

> hw = hardware

### 目的
確保整個系統中 LCD / IMU / Touch 只建立一次，  
避免重複初始化造成記憶體耗盡或 I2C 裝置衝突。

### 使用方式
```python
from hw import LCD, IMU, TP
```

### 為什麼推薦 hw.py
- LCD FrameBuffer 佔用 115200 bytes
- RP2040 heap 有限，重複配置會直接 MemoryError
- hw.py 在架構層級防止錯誤，而不是靠人記得「不要 new LCD」

---

## /lib/menu.py — 圓形表盤 Launcher / Menu

### 功能
- 掃描裝置內的 `.py` 檔案
- 以圓形表盤方式顯示
- 支援滑動切換、點選執行
- 使用 exec() 執行腳本
- 防止被執行腳本重複初始化 LCD / Touch

### 設計重點
- LCD 單例（唯一 FrameBuffer）
- Touch 單例
- 記憶體保護（GC / monkey patch）
- Menu 為系統核心，不是 App

---

## /main.py — 系統進入點

唯一用途：啟動 Menu

```python
import menu
menu.main()
```

---

## 腳本撰寫規範（非常重要）

### 錯誤寫法（會導致 MemoryError）
```python
import touch
LCD = touch.LCD_1inch28()
```

### 推薦寫法（可單跑、可被 Menu 執行）
```python
import touch

try:
    LCD
except NameError:
    LCD = touch.LCD_1inch28()
    LCD.set_bl_pwm(15535)
```

或（若使用 hw.py）：

```python
from hw import LCD
```

---

## 記憶體限制說明

- LCD FrameBuffer：240 × 240 × 2 = 115200 bytes
- RP2040 MicroPython heap 約 240 KB
- 同時存在 2 個 LCD FrameBuffer 幾乎必定爆 RAM

---

## 架構總結

```
main.py
  ↓
menu.py   ← Launcher / 記憶體守門人
  ↓
hw.py     ← 硬體單例層（可選）
  ↓
touch.py  ← Driver 層
```

---

## 設計哲學（給未來的自己）

- 大物件只建一次
- 硬體初始化集中
- Launcher 是系統，不是 App
- 避免「記得不要 new」這種人為約定

---

## 常見錯誤快速檢查

- MemoryError allocating 115200 bytes  
  → 某處又 new 了 LCD
- Not Detected CST816T  
  → Touch 腳位用到錯誤預設值
- Menu 能顯示但腳本一點就炸  
  → 腳本自行初始化硬體
