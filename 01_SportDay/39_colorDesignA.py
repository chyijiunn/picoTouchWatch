#加入選色功能，滑入右方進入選色
from machine import Pin, SPI, ADC
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
color = LCD.color

class Point:
    def __init__(self,x,y):
        self.X=x
        self.Y=y
    def __str__(self):
        return "Point(%s,%s)"%(self.X,self.Y)
        
class Triangle:
    def __init__(self,p1,p2,p3):
        self.P1=p1
        self.P2=p2
        self.P3=p3

    def __str__(self):
        return "Triangle(%s,%s,%s)"%(self.P1,self.P2,self.P3)
    
    def draw(self):
        print("I should draw now")
        self.fillTri()
      
    def sortVerticesAscendingByY(self):    
        if self.P1.Y > self.P2.Y:
            vTmp = self.P1
            self.P1 = self.P2
            self.P2 = vTmp
        
        if self.P1.Y > self.P3.Y:
            vTmp = self.P1
            self.P1 = self.P3
            self.P3 = vTmp

        if self.P2.Y > self.P3.Y:
            vTmp = self.P2
            self.P2 = self.P3
            self.P3 = vTmp
        
    def fillTri(self):
        self.sortVerticesAscendingByY()
        if self.P2.Y == self.P3.Y:
            fillBottomFlatTriangle(self.P1, self.P2, self.P3)
        else:
            if self.P1.Y == self.P2.Y:
                fillTopFlatTriangle(self.P1, self.P2, self.P3)
            else:
                newx = int(self.P1.X + (float(self.P2.Y - self.P1.Y) / float(self.P3.Y - self.P1.Y)) * (self.P3.X - self.P1.X))
                newy = self.P2.Y                
                pTmp = Point( newx,newy )
                fillBottomFlatTriangle(self.P1, self.P2, pTmp)
                fillTopFlatTriangle(self.P2, pTmp, self.P3)

def fillBottomFlatTriangle(p1,p2,p3):
    if p2.Y > p3.Y:
        ty = p3.Y
        p3.Y = p2.Y
        p2.Y = ty
        tx = p3.X
        p3.X = p2.X
        p2.X = tx
        print(p1,p2,p3)
    
    slope1 = float(p2.X - p1.X) / float (p2.Y - p1.Y)
    slope2 = float(p3.X - p1.X) / float (p3.Y - p1.Y)

    x1 = p1.X
    x2 = p1.X + 0.5

    for scanlineY in range(p1.Y,p2.Y):
        LCD.hline(int(x1),scanlineY, int(x2)-int(x1),c)        
        LCD.hline(int(x2),scanlineY, -(int(x2)-int(x1)),c)

        x1 += slope1
        x2 += slope2

def fillTopFlatTriangle(p1,p2,p3):
    slope1 = float(p3.X - p1.X) / float(p3.Y - p1.Y)
    slope2 = float(p3.X - p2.X) / float(p3.Y - p2.Y)
    x1 = p3.X
    x2 = p3.X + 0.5

    for scanlineY in range (p3.Y,p1.Y-1,-1):
        LCD.hline(int(x1),scanlineY, int(x2)-int(x1)+1,c)        
        LCD.hline(int(x2),scanlineY, -(int(x2)-int(x1)-1),c)
        x1 -= slope1
        x2 -= slope2

def triangle(x1,y1,x2,y2,x3,y3,c): 
    LCD.line(x1,y1,x2,y2,c)
    LCD.line(x2,y2,x3,y3,c)
    LCD.line(x3,y3,x1,y1,c)
    
def tri_filled(x1,y1,x2,y2,x3,y3,c): 
    t=Triangle(Point(x1,y1),Point(x2,y2),Point(x3,y3))
    t.fillTri()

def spin(value,base_length,r,c):#針底部寬度、長度、顏色
    spinBottomx_shift = int(base_length*math.sin(math.radians(value+90)))
    spinBottomy_shift = int(base_length*math.cos(math.radians(value+90)))
    spinTopX_shift = int(r*math.sin(math.radians(value)))
    spinTopY_shift = int(r*math.cos(math.radians(value)))
            
    tri_filled(cx+spinTopX_shift,cy-spinTopY_shift,cx+spinBottomx_shift,cy-spinBottomy_shift,cx-spinBottomx_shift,cy+spinBottomy_shift,c)

def watch():
    global c , now
    now = list(time.localtime())
    x_shift = int(secspin*math.sin(math.radians(6*now[5])))
    y_shift = int(secspin*math.cos(math.radians(6*now[5])))
    c = hourspincolor
    spin((30*now[3]+0.5*now[4]),4,hourspin,c)#hour
    c = minspincolor
    spin((6*now[4]+0.1*now[5]),3,minspin,c)#min
    c = seccolor
    LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)#sec
    '''
    LCD.write_text(str(now[2]),110,20,3,color(255,255,255))#date
    LCD.write_text(day(),160,40,2,daycolor())#星期幾
    '''
    LCD.write_text('{:0>2}:'.format(now[3])+'{:0>2}'.format(now[4]),110,90,2,digitimecolor)#digitalClock:hour , min
    LCD.write_text('{:0>2}'.format(now[5]),190,90,3,digiseccolor)#digitalClock:sec
    LCD.show()
    c = BG
    spin((30*now[3]+0.5*now[4]),4,hourspin,c)
    spin((6*now[4]+0.1*now[5]),3,minspin,c)
    LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)
    LCD.fill_rect(110,90,80,14,c)#digitalClock refresh
    LCD.fill_rect(190,90,60,30,c)

def day():
    key = now[6]
    day = ['MON','TUE','WED','THU','FRI','SAT','SUN']
    return day[key]

def daycolor():
    if now[6] == 5 : daycolor = color(0,255,0)
    elif now[6] == 6 : daycolor = color(255,0,0)
    else : daycolor = color(255,255,255)
    return daycolor
                
def circle(cx,cy,r,color):
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <=  r*r :
                LCD.pixel(cx+i,cy+j,color)
    
def Ring(cx, cy , thick , r , color):
    for i in range(-(r+thick),r+thick,1):
        for j in range(-(r+thick),r+thick,1):
            if (i*i + j*j <  (r+thick)*(r+thick) )and (i*i + j*j > r*r):
                LCD.pixel(cx+i,cy+j,color)

def runDotRing(cx, cy , thick , reach , r , color):
    x = int(r*math.sin(math.radians(reach*360)))
    y = int(r*math.cos(math.radians(reach*360)))
    for i in range(-thick,thick,1):
        for j in range(-thick,thick,1):
            if i*i + j*j <=  r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
                
def BackRunDotRing(cx, cy , thick , reach , r , color):
    x = int(r*math.sin(math.radians(reach*360)))
    y = int(r*math.cos(math.radians(reach*360)))
    for i in range(-thick,thick,1):
        for j in range(-thick,thick,1):
            if i*i + j*j <=  (r+thick)*(r+thick):
                LCD.pixel(cx+x+i,cy-y+j,color)

def refresh():
    LCD.fill_rect(182,173,10,10,BG)#右圈
    LCD.fill_rect(113,173,25,10,BG)#中圈
    LCD.fill_rect(42,173,10,10,BG)#右圈
    LCD.fill_rect(120,70,80,10,BG)#右上長條1刷除
    LCD.fill_rect(120,58,80,10,BG)#右上長條2 backlight 刷除
    
def littlefuntion():
    global walknum , runnum , walkTARGET , runTARGET ,backlight
    xyz=touch.QMI8658().Read_XYZ()
    N1 = xyz[5]
    xyz=touch.QMI8658().Read_XYZ()
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
    runDotRing(192,180,2,walkreach,25,color(255,125,125))
    LCD.write_text(str(int(walkreach*100)), 182, 173,1,FG)
    
    #中圈：電力資料
    reading = ADC(Pin(29)) .read_u16()*3.3/65535*2
    full = 2.75
    if reading > full : reading = full 
    bat_remain = (reading - 2.25 ) / (full -2.25)  #(測得電壓-終止電壓)除以(飽和電壓-終止電壓)
    BackRunDotRing(120,180,3,bat_remain,25,BG)
    LCD.write_text(str(int(bat_remain*100)), 110, 178,1,FG)
    LCD.fill_rect(120,58,int(backlight/65535*80),10,seccolor)#右上長條2 backlight 長度配秒針顏色
    LCD.fill_rect(120,70,int(bat_remain*80),10,BATcolor)#右上長條2繪製 BAT 長度
    
    #電壓測試資料
    '''
    data = open('record','a')
    now = list(time.localtime())
    data.write(str(now[3])+':'+str(now[4])+':'+str(now[5])+'-'+str("{:.2f}".format(reading))+'\n')
    data.close()
    '''
    #左圈：跑步資料
    runDotRing(52,180,2,runreach,25,color(125,255,125))
    LCD.write_text(str(int(runreach*100)), 42, 173,1,FG)
    return bat_remain

def stoptime():
    N1 = time.ticks_ms()#Start 時刻
    digitalxstart = 60
    digitalystart = 130
    R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))
    FC = color(R,G,B)
    circle(120,180,23,BG)#電力中圈抹除
    LCD.show()

    while True:
        LCD.fill_rect(digitalxstart,digitalystart,160,15,BG)#stoptime refresh
        
        xyz0 = touch.QMI8658().Read_XYZ()#Data_ini
        N2 = time.ticks_ms()-N1#End 時刻
        cS = int(N2//10)#百分秒
        S = int(N2 //1000)#秒
        M =int(S//60)#分
        H =int(M//60)#時
        now = str(H)+':'+str(M%60)+':'+str(S%60)+'.'+str(cS%100)
        x_shift = int(20*math.sin(math.radians(3.6*cS)))
        y_shift = int(20*math.cos(math.radians(3.6*cS)))
        LCD.write_text(now,digitalxstart,digitalystart,2,FC)
        LCD.line(120,180,120+x_shift,180-y_shift,FC)#秒錶跳動
        LCD.show()
        LCD.line(120,180,120+x_shift,180-y_shift,BG)#秒錶更新
        if xyz0[1] < -0.95 :break#y軸近垂直於地面，左手朝上
    
def showvarycolor():
    for i in range(0,255,20):
        for j in range(0,255,20):
            LCD.fill_rect(i,j,20,20,color(i,j,125))
    LCD.show()

def pickcolor():
    Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
    x = y  = 0
    Touch.Flgh = 0
    Touch.Flag = 0
    Touch.tim.init(period=1, callback=Touch.Timer_callback)
    while True:
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            return x , y 
            break
        
def colorini():
    global colorR , colorG , colorB , c_colorR , c_colorG , c_colorB,tickmark_h_color,tickmark_m_color,BATcolor , seccolor, minspincolor, hourspincolor,digiseccolor,digitimecolor
    c_colorR , c_colorG , c_colorB = 255-colorR , 255-colorG, 255-colorB
    tickmark_h_color = color(c_colorR,c_colorG,c_colorB)
    tickmark_m_color = color(c_colorR,c_colorG,c_colorB)
    seccolor , minspincolor , hourspincolor =color(colorR,225,0),color(255,colorG,125) ,color(255,colorG,125)
    digiseccolor , digitimecolor = seccolor , hourspincolor
    BATcolor = color(125,255,125)
    
backlight = 35535
LCD.set_bl_pwm(backlight)
BG = color(0,0,0)
FG = color(255,255,255)
colorR , colorG , colorB = random.randint(125,255),random.randint(125,255) ,random.randint(125,255)

#錶盤大小
platesize = 40
#錶盤中心點
cx , cy  = 70 ,70
#定義時、分刻度線
tickmark_h , tick_mark_m = platesize-3 , platesize

#針長度、顏色
secspin ,minspin , hourspin = tickmark_h-5,platesize - 4 ,platesize/2

walknum = 0
walkTARGET = 100 # 每天要走幾步
runnum = 0
runTARGET = 100 # 每天要跑幾步
threhold = 300
now = list(time.localtime())

def plateini():
    LCD.fill(BG)
    for i in range(60):#先畫分刻度線
        LCD.line(cx+int(tick_mark_m*math.sin(math.radians(6*i))),cy-int(tick_mark_m*math.cos(math.radians(6*i))),cx+int(platesize*math.sin(math.radians(6*i))),cy-int(platesize*math.cos(math.radians(6*i))),tickmark_m_color)
    for i in range(12):#再畫時刻度線
        LCD.line(cx+int(tickmark_h*math.sin(math.radians(30*i))),cy-int(tickmark_h*math.cos(math.radians(30*i))),cx+int(platesize*math.sin(math.radians(30*i))),cy-int(platesize*math.cos(math.radians(30*i))),tickmark_h_color)

    LCD.write_text(str(now[1])+'/'+str(now[2]),112,105,1,color(255,255,255))#date
    LCD.write_text(day(),162,105,1,daycolor())#星期幾
    #中圈環狀
    Ring(120,180,2,23,BATcolor)
    LCD.show()
    
colorini()#初始化顏色設定
plateini()#初始化錶盤設定

while True:
    if Touch.Gestures == 0x0C:#長按，改背景色，點第二下才能選色
        Touch.Gestures = 'none'
        Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
        LCD.fill(BG)
        showvarycolor()
        while pickcolor() != 0:
            colorR , colorG = pickcolor()
            break
        Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
        BG = color(colorR,colorG,125)
        colorini()
        plateini()
        
        
    if Touch.Gestures == 0x03:#滑入右，休眠
        LCD.sleep_mode(1)
        LCD.set_bl_pwm(0)
        Touch.Gestures = 'none'
        
    if touch.QMI8658().Read_XYZ()[0] <= -0.7:#錶面朝自己傾斜超過 x <= -.7
        LCD.sleep_mode(0)
        LCD.set_bl_pwm(backlight)
        Touch.Gestures = 'none'
        
    if Touch.Gestures == 0x01:#向上滑，+ 亮度
        backlight = backlight + 3000
        if backlight > 65535:backlight = 65535
        LCD.set_bl_pwm(backlight)
        Touch.Gestures = 'none'
    if Touch.Gestures == 0x02:#向下滑，- 亮度
        backlight = backlight - 5000
        if backlight < 1:backlight = 1
        LCD.set_bl_pwm(backlight)
        Touch.Gestures = 'none'
    if Touch.Gestures == 0x04:#滑入左，碼表開啟
        Touch.Gestures = 'none'
        stoptime()
         
    else:
        watch()
        refresh()
        littlefuntion()