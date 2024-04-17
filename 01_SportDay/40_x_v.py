#根據跑步資料和走路資料的時間來估量距離，不準，未完成
import time , touch, math , random
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
qmi8658 = touch.QMI8658()
color = LCD.color
LCD.set_bl_pwm(30000)

walknum = 0
runnum = 0

def movedata():
    global walknum, runnum
    while 1:
        N1 = qmi8658.Read_XYZ()
        time.sleep(0.05)
        N2=qmi8658.Read_XYZ()
    
        if N1[5]*N2[5] < 0:
            if (N2[3]> 100) and (N2[3] <  150) :
                walknum = walknum + 1
            elif ((N2[3]> -50) and (N2[3] <  100) )or  ((N2[3]> 150) and (N2[3] <  270) ) and  N2[1]< - 0.8:
                runnum = runnum + 1
        if Touch.Gestures == 0x04:break
    
    return walknum , runnum
            
def distant(dataname):
    data = open(str(dataname),'a')
    while Touch.Gestures != 0x03:pass
    N1 = time.ticks_ms()
    out = movedata()
    N2 = time.ticks_ms
    data.write(str((N2-N1)/1000)+':'+str(out))
    data.close()
    
for i in range(2):
    distant(i)
