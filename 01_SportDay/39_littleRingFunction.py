# 為了修改環的位置，寫成函式，並加入電池資料
from machine import Pin , ADC
import time , touch, math

LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(15535)
color = LCD.color

#電池資料
Vbat_Pin = 29
Vbat= ADC(Pin(Vbat_Pin)) 
LCD.fill(color(0,0,0))

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

# 電量為遞減資料：
# 先畫一個環，不能放在 while 迴圈
# 改為遞減，畫背景以抹除原本的環

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
Ring(120,180,2,23,color(0,200,0))

while 1:
    xyz=qmi8658.Read_XYZ()
    N1 = xyz[5]
    now = list(time.gmtime())
    #time
    LCD.write_text('{0:0>2}:{1:0>2}:{2:0>2}'.format(now[3],now[4],now[5]),55,100,2,color(0,0,0))
    xyz=qmi8658.Read_XYZ()
    N2 = xyz[5]
    
    if N1*N2 < 0:
        if (N1>10 and N1<threhold) or (N2>10 and N2<threhold):
            walknum = walknum + 1
        elif (N1 or N2) > threhold or (N1 or N2)< -threhold :
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
    runDotRing(192,180,2,walkreach,25,color(colorfactorW,colorfactorW,100))
    LCD.write_text(str(int(walkreach*100)), 182, 173,1,color(255,255,255))
    
    #中圈：電力資料
    reading = Vbat.read_u16()*3.3/65535*2
    bat_remain = (reading - 2.25 ) / (2.75-2.25)  #(測得電壓-終止電壓)除以(飽和電壓-終止電壓)
    BackRunDotRing(120,180,3,bat_remain,25,color(0,0,0))#黑色為抹除資料
    LCD.show()
    LCD.write_text(str(int(bat_remain*100)), 113, 173,1,color(255,255,255))
    
    #左圈：跑步資料
    runDotRing(52,180,2,runreach,25,color(100,colorfactorR,colorfactorR))
    LCD.write_text(str(int(runreach*100)), 42, 173,1,color(255,255,255))