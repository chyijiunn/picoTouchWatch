from machine import Pin, SPI
import random ,utime ,touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(10000)

N1 = utime.ticks_ms()# 讀取 utime.ticks_ms() 存為 N1
digitalxstart = 60
digitalystart = 100

R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

#設定前景色與背景色
BG = LCD.color(R,G,B)
FC = LCD.color(120,120,120)

while True:
    N2 = utime.ticks_ms()-N1# 讀取 utime.ticks_ms() 減去 N1 存為 N2
    cS = int(N2//10)#百分秒，捨棄千分位，使用 // 10 得到商，轉為整數
    S = int(N2 //1000)#秒，取個位，使用 // 1000 得到商，轉為整數
    M =int(S//60)#分，根據累積的秒 // 60 得到商，轉整數
    H =int(M//60)#時，根據累積的分 // 60 得到商，轉整數
    
    # 將上述資料轉字串外
    # 分鐘顯示為餘數資料，以 % 計算，秒數亦同，
    # 百分秒取 %100 的餘數
    now = str(H)+':'+str(M%60)+':'+str(S%60)+'.'+str(cS%100)
    LCD.fill(BG)
    LCD.text(now,digitalxstart,digitalystart,FC)
    LCD.show()
