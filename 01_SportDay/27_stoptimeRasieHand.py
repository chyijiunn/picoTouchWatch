import touch,utime,random
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)

color = LCD.color
LCD.set_bl_pwm(35535)

def stoptime_main():
    Touch.Gestures = 'none'
    R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))
    BG = color(R,G,B)
    FC = color(255-R,255-G,255-B)
    LCD.fill(BG)
    N1 = utime.ticks_ms()#Start 時刻
    digitalxstart = 20
    digitalystart = 100

    while True:
        LCD.fill_rect(digitalxstart,digitalystart,210,25,BG)#數字refresh
        xyz = touch.QMI8658().Read_XYZ()
        N2 = utime.ticks_ms()-N1#End 時刻
        cS = int(N2//10)#百分秒
        S = int(N2 //1000)#秒
        M =int(S//60)#分
        H =int(M//60)#時
        now = str(H)+':'+str(M%60)+':'+str(S%60)+'.'+str(cS%100)
        LCD.write_text(now,digitalxstart,digitalystart,3,FC)
        LCD.show()
        
        if xyz[1] < -0.95 :break#y軸近垂直於地面，左手朝上
        
    LCD.write_text('TimeUP',70,digitalystart+40,2,FC)
    LCD.show()
    
while Touch.Gestures != 0x03:
    LCD.fill(LCD.black)
    LCD.write_text('SlideRight',45,125,2,color(90,180,40))
    LCD.write_text('Enter StopTime',70,150,1,color(90,180,40))
    LCD.show()
    
LCD.fill(LCD.black)
LCD.show()

stoptime_main() 
