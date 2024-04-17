# 加跑步資料，列為內圈
import time , touch, math
LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(30000)

cx , cy =120 ,120
walknum = 0
walkTARGET = 5000 # 每天要走幾步
runnum = 0
runTARGET = 1000 # 每天要跑幾步
                
def runDotRing(r , walkreach , spinLen , color):
    x = int(spinLen*math.sin(math.radians(walkreach*360)))
    y = int(spinLen*math.cos(math.radians(walkreach*360)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)

def color(R,G,B):
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

while 1:
    N1 = qmi8658.Read_XYZ()
    time.sleep(0.05)
    N2=qmi8658.Read_XYZ()
    
    if N1[5]*N2[5] < 0:#這裡以個人的資料來定義
        if (N2[3]> 100) and (N2[3] <  150) :
            walknum = walknum + 1
        elif ((N2[3]> -50) and (N2[3] <  100) )or  ((N2[3]> 150) and (N2[3] <  270) ) and  N2[1]< - 0.8:
            runnum = runnum + 1
            
    walkreach = walknum/walkTARGET
    runreach = runnum/runTARGET
    
    runDotRing(12,walkreach,110,color(walknum,180,walknum))#走路外圈，點繞行
    runDotRing(12,runreach,88,color(runnum,180,180))#跑步內圈資料
    
    LCD.text(str(int(walkreach*100))+'%'+str(walknum),110,120,color(int(walkreach*128),180,int(walkreach*128)))
    LCD.text(str(int(runreach*100))+'%'+str(runnum),110,100,color(int(runreach*128),180,180))
    
    LCD.show()
    LCD.fill_rect(110,100,50,30,LCD.white)

