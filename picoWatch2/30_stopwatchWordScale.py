from machine import Pin, SPI
import random ,utime ,touch
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

N1 = utime.ticks_ms()
digitalxstart = 60
digitalystart = 100

R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

BG = LCD.color(R,G,B)
FC = LCD.color(255-R,255-G,255-B)#改為互補色
print(R,G,B)
while True:
    N2 = utime.ticks_ms()-N1
    cS = int(N2//10)
    S = int(N2 //1000)
    M =int(S//60)
    H =int(M//60)
    now = str(H)+':'+str(M%60)+':'+str(S%60)+'.'+str(cS%100)
    LCD.fill(BG)
    #write_text，增加一個字大小的引數
    LCD.write_text(now,digitalxstart,digitalystart,2,FC)
    LCD.show()
