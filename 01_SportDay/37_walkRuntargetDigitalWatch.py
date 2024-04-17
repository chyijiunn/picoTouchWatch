# 加上跑步資料在內圈
# 根據 32_recorderFunction.py 的 data 修正條件式 line 35
import time , touch, math
LCD = touch.LCD_1inch28()
qmi8658 = touch.QMI8658()
LCD.set_bl_pwm(15535)
color = LCD.color

LCD.fill(color(0,0,0))

cx , cy =120 ,120
walknum = 0
walkTARGET = 100 # 每天要走幾步
runnum = 0
runTARGET = 100 # 每天要跑幾步
threhold = 300

def runDotRing(reach , spinLen , color):
    r = 12
    x = int(spinLen*math.sin(math.radians(reach*360)))
    y = int(spinLen*math.cos(math.radians(reach*360)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
while 1:
    xyz=qmi8658.Read_XYZ()
    N1 = xyz[5]
    now = list(time.gmtime())
    LCD.write_text('{0:0>2}:{1:0>2}:{2:0>2}'.format(now[3],now[4],now[5]),60,120,2,color(255,225,0))
    LCD.show()
    LCD.fill_rect(60,120,130,20,color(0,0,0))
    xyz=qmi8658.Read_XYZ()
    N2 = xyz[5]
    
    if N1*N2 < 0:#個人化條件式
        if (N1>10 and N1<threhold) or (N2>10 and N2<threhold):
            walknum = walknum + 1
        elif (N1 or N2) > threhold or (N1 or N2)< -threhold :
            runnum = runnum + 1
            
    walkreach = walknum/walkTARGET
    runreach = runnum/runTARGET
    colorfactorW = int(255*(1-walkreach))
    colorfactorR = int(255*(1-runreach))
    
    runDotRing(walkreach,110,color(colorfactorW,200,colorfactorW))
    runDotRing(runreach,88,color(100,colorfactorR,colorfactorR))
