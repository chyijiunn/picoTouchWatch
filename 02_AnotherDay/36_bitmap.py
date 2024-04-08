from machine import Pin, SPI
import touch , bmp #記得引入 bmp
import gc9a01py as gc9a01

spi = SPI(1, baudrate=62500000, sck=Pin(10), mosi=Pin(11))
LCD = gc9a01.GC9A01(spi,dc=Pin(8, Pin.OUT),cs=Pin(9, Pin.OUT),reset=Pin(12, Pin.OUT),backlight=Pin(25, Pin.OUT),rotation=0)
color = gc9a01.color565

LCD.fill(color(225,225,0))
# LCD.bitmap(檔名.py,起始 x ,起始 y)
LCD.bitmap(bmp,90,90)