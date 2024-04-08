# 讀取走路的角加速度差異值，並記錄
# 記錄
#     1.utime.ticks_ms() 時間差
#     2.同時呈現碼錶面資料
#     3.角加速度 - 利用手部晃動時，若加速度發生正負變換，就記錄

import random ,utime , touch
LCD = touch.LCD_1inch28()
qmi8658=touch.QMI8658()

N1 = utime.ticks_ms()#Start 時刻
digitalxstart = 60
digitalystart = 100
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))
BG = LCD.color(R,G,B)
FC = LCD.color(256-R,256-G,256-B)
LCD.fill(BG)

data = open('record_fix.csv','a')

while True:
    xyz0 = qmi8658.Read_XYZ()#Data_ini
    N2 = utime.ticks_ms()-N1#End 時刻
    cS = int(N2//10)#百分秒
    S = int(N2 //1000)#秒
    M =int(S//60)#分
    H =int(M//60)#時
    now = str(H)+':'+str(M%60)+':'+str(S%60)+'.'+str(cS%100)
    LCD.text(now,digitalxstart,digitalystart,FC)
    LCD.show()
    xyz1 = qmi8658.Read_XYZ()#Data_Final
    
    print(now,',',xyz1[3]-xyz0[3],',',xyz1[4]-xyz0[4],',',xyz1[5]-xyz0[5])

    if xyz1[5]*xyz0[5]<0:#為了看出區別，放大scale
        data.write(str(now)+','+str(round(1000*xyz1[0],3)) +','+str(1000*round(xyz1[1],3))+','+str(1000*round(xyz1[2],3))+','+str(round(100*(xyz1[3]-xyz0[3]),2))+','+str(round(100*(xyz1[4]-xyz0[4]),2))+','+str(round(100*(xyz1[5]-xyz0[5]),2))+'\n')
        #data.write(str(now)+','+str(round(xyz1[3]-xyz0[3],2))+','+str(round(xyz1[4]-xyz0[4],2))+','+str(round(xyz1[5]-xyz0[5],2))+'\n')