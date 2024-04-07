# 錶面和時間結合在一起
from machine import Pin, SPI
from fonts import vga2_16x32 as font
import time , bmp #記得引入 轉檔後 檔名
import gc9a01py as gc9a01

spi = SPI(1, baudrate=62500000, sck=Pin(10), mosi=Pin(11))
LCD = gc9a01.GC9A01(spi,dc=Pin(8, Pin.OUT),cs=Pin(9, Pin.OUT),reset=Pin(12, Pin.OUT),backlight=Pin(25, Pin.OUT),rotation=0)
color = gc9a01.color565

LCD.fill(color(255,225,0))
LCD.bitmap(bmp,90,90)
while 1:
    now = list(time.gmtime())
    #LCD._text16(font,str(now[3])+':'+str(now[4])+':'+str(now[5]),60,160,color(0,0,0),color(255,225,0))
    LCD._text16(font,'{0:0>2}:{1:0>2}:{2:0>2}'.format(now[3],now[4],now[5]),60,160,color(0,0,0),color(255,225,0))
