# 搭配前面蝙蝠俠，改了顏色
from machine import Pin, SPI, ADC
from fonts import vga2_16x32 as fontL
from fonts import vga2_8x16 as fontS
import time  ,math,RP,bmp#記得引入 轉檔後 檔名
import gc9a01py as gc9a01

spi = SPI(1, baudrate=62500000, sck=Pin(10), mosi=Pin(11))
LCD = gc9a01.GC9A01(spi,dc=Pin(8, Pin.OUT),cs=Pin(9, Pin.OUT),reset=Pin(12, Pin.OUT),backlight=Pin(25, Pin.OUT),rotation=0)
color = gc9a01.color565
qmi8658 = RP.QMI8658()
Vbat_Pin = 29
Vbat= ADC(Pin(Vbat_Pin)) 

BG = color(255,225,0)
FG = color(0,0,0)
LCD.fill(BG)
LCD.bitmap(bmp,90,90)

walknum = 0
walkTARGET = 100 # 每天要走幾步
runnum = 0
runTARGET = 100 # 每天要跑幾步
threhold = 300

def runDotRing(cx, cy , thick , reach , r , color):
    x = int(r*math.sin(math.radians(reach*360)))
    y = int(r*math.cos(math.radians(reach*360)))
    for i in range(-thick,thick,1):
        for j in range(-thick,thick,1):
            if i*i + j*j <=  r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
                
def Ring(cx, cy , thick , r , color):
    for i in range(-(r+thick),r+thick,1):
        for j in range(-(r+thick),r+thick,1):
            if (i*i + j*j <  (r+thick)*(r+thick) )and (i*i + j*j > r*r):
                LCD.pixel(cx+i,cy+j,color)
                
def BackRunDotRing(cx, cy , thick , reach , r , color):
    x = int(r*math.sin(math.radians(reach*360)))
    y = int(r*math.cos(math.radians(reach*360)))
    for i in range(-thick,thick,1):
        for j in range(-thick,thick,1):
            if i*i + j*j <=  (r+thick)*(r+thick):
                LCD.pixel(cx+x+i,cy-y+j,color)
                
#中圈環狀
Ring(120,180,2,23,color(255,255,255))

while 1:
    xyz=qmi8658.Read_XYZ()
    N1 = xyz[5]
    now = list(time.gmtime())
    #time
    LCD._text16(fontL,'{0:0>2}:{1:0>2}:{2:0>2}'.format(now[3],now[4],now[5]),55,60,FG,BG)
    xyz=qmi8658.Read_XYZ()
    N2 = xyz[5]
    y = xyz[1]
    if N1*N2 < 0:
        if (N1>10 and N1<threhold) or (N2>10 and N2<threhold):
            walknum = walknum + 1
        elif (((N1 or N2) > threhold) or ((N1 or N2)< -threhold))and y < - 0.8 :
            runnum = runnum + 1
            
    walkreach = walknum/walkTARGET
    runreach = runnum/runTARGET
    colorfactorW = int(255*(walkreach))
    colorfactorR = int(255*(runreach))
    '''顏色顛倒
    colorfactorW = int(255*(1-walkreach))
    colorfactorR = int(255*(1-runreach))
    '''
    #右圈：走路資料
    runDotRing(192,180,2,walkreach,25,color(255,255,255))
    LCD.text(fontS, str(int(walkreach*100)), 182, 173,FG,BG)
    
    #中圈：電力資料
    reading = Vbat.read_u16()*3.3/65535*2
    bat_remain = (reading - 3.37 ) / (4.1-3.37)  #(測得電壓-終止電壓)除以(飽和電壓-終止電壓)
    BackRunDotRing(120,180,3,bat_remain,25,BG)
    LCD.text(fontS, str(int(bat_remain*100)), 113, 173,FG,BG)
    
    #左圈：跑步資料
    runDotRing(52,180,2,runreach,25,color(255,255,255))
    LCD.text(fontS, str(int(runreach*100)), 42, 173,FG,BG)
    
