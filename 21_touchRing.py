'''
盤面左邊和右邊往上與往下有不同的結果
利用 x >120 or <120
再針對時間間隔 0.01秒時的觸控y座標差異做出環的移動
'''
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
BG = color(0,0,0)
FG = color(255,255,255)
c1 = color(55,25,125)
c2 = color(255,225,255)

xstart,ystart,xlen,ylen = 80,160 , 80 , 20#scrollBar setting
cx , cy = 120,120#scrollRing setting 

Touch.Flag = 0
Touch.Mode = 1
Touch.Set_Mode(Touch.Mode)

def scrollBar():
    x = y = data = 0
    color = 0

    while True:
        LCD.fill_rect(xstart,ystart,xlen,ylen,c1)
        if Touch.Flag == 1:
            x = Touch.X_point
            y = Touch.Y_point
            if x-xstart > xlen: x = xstart + xlen
            LCD.fill_rect(xstart,ystart,x-xstart,ylen,c2)
            LCD.show()
            print(x,y)
            
def Ring(cx, cy , thick , r , color):
    for i in range(-(r+thick),r+thick,1):
        for j in range(-(r+thick),r+thick,1):
            if (i*i + j*j <  (r+thick)*(r+thick) )and (i*i + j*j > r*r):
                LCD.pixel(cx+i,cy+j,color)
                
def BackRunDotRing(cx, cy , thick , goal_percent , r , color):
    x = int(r*math.sin(math.radians(goal_percent*360)))
    y = int(r*math.cos(math.radians(goal_percent*360)))
    for i in range(-thick,thick,1):
        for j in range(-thick,thick,1):
            if i*i + j*j <=  (r+thick)*(r+thick):
                LCD.pixel(cx+x+i,cy-y+j,color)

def scrollRing():
    LCD.fill(BG)
    Ring(cx,cy,8,100,c2)
    LCD.show()
    converty = 1
    while 1:
        if Touch.Flag == 1:
            x0 = Touch.X_point
            y0 = Touch.Y_point
            time.sleep(0.01)
            #x1 = Touch.X_point
            y1 = Touch.Y_point
            
            if x0<120 :
                if y1 > y0:converty = converty - 0.01
                elif y1 < y0: converty = converty + 0.01
            elif x0>120:
                if y1 < y0:converty = converty - 0.01
                elif y1 > y0: converty = converty + 0.01
            Touch.Flag = 0
            BackRunDotRing(cx,cy,10,converty,100,BG)
            print(y0,y1,converty)
            LCD.show()
    

scrollRing()
