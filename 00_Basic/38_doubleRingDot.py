# 加跑步資料，列為內圈
import time , touch, math
LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(30000)

cx , cy =120 ,120
walknum = 0
walkTARGET = 100 # 每天要走幾步
runnum = 0
runTARGET = 100 # 每天要跑幾步

threhold = 300 #設立閾值
                
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
    
    xyz=qmi8658.Read_XYZ()
    N1 = xyz[5]
    time.sleep(0.05)
    xyz=qmi8658.Read_XYZ()
    N2 = xyz[5]
    y = xyz[1]
    if N1*N2 < 0:#這裡以個人的資料來定義
        if (N1>10 and N1<threhold) or (N2>10 and N2<threhold):
            walknum = walknum + 1
        elif (((N1 or N2) > threhold) or ((N1 or N2)< -threhold)) and y < - 0.8:
            runnum = runnum + 1
            
    walkreach = walknum/walkTARGET
    runreach = runnum/runTARGET
    
    runDotRing(12,walkreach,110,color(walknum,180,walknum))#走路外圈，點繞行
    runDotRing(12,runreach,88,color(runnum,180,180))#跑步內圈資料
    
    LCD.text(str(int(walkreach*100))+'%'+str(walknum),110,120,color(int(walkreach*128),180,int(walkreach*128)))
    LCD.text(str(int(runreach*100))+'%'+str(runnum),110,100,color(int(runreach*128),180,180))
    
    LCD.show()
    LCD.fill_rect(110,100,50,30,LCD.white)

