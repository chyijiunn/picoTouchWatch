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
    global c
    now = list(time.localtime())
    x_shift = int(secspin*math.sin(math.radians(6*now[5])))
    y_shift = int(secspin*math.cos(math.radians(6*now[5])))
    c = hourspincolor
    spin((30*now[3]+0.5*now[4]),4,hourspin,c)#hour
    c = minspincolor
    spin((6*now[4]+0.1*now[5]),3,minspin,c)#min
    c = seccolor
    LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)#sec
    LCD.show()
    c = BG
    spin((30*now[3]+0.5*now[4]),4,hourspin,c)
    spin((6*now[4]+0.1*now[5]),3,minspin,c)
    LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)

def showcolor():
    Touch.Set_Mode(1)
    BG = color(0,0,0)
    LCD.fill(BG)
    for i in range(0,255,20):
        for j in range(0,255,20):
            LCD.fill_rect(i,j,20,20,color(i,j,125))
    LCD.show()
    
LCD.set_bl_pwm(15535)
BG = color(0,0,0)
LCD.fill(BG)
#錶盤大小
platesize = 40
#錶盤中心點
cx , cy  = 70 ,70
#定義時、分刻度線
tickmark_h , tick_mark_m = platesize-3 , platesize
tickmark_h_color = color(255,100,0)
tickmark_m_color = color(255,0,0)
#針長度、顏色
secspin ,minspin , hourspin = tickmark_h-5,platesize ,platesize/2
seccolor , minspincolor , hourspincolor =color(250,225,0),color(200,100,0) ,color(250,50,125)

for i in range(60):#先畫分刻度線
    LCD.line(cx+int(tick_mark_m*math.sin(math.radians(6*i))),cy-int(tick_mark_m*math.cos(math.radians(6*i))),cx+int(platesize*math.sin(math.radians(6*i))),cy-int(platesize*math.cos(math.radians(6*i))),tickmark_m_color)
for i in range(12):#再畫時刻度線
    LCD.line(cx+int(tickmark_h*math.sin(math.radians(30*i))),cy-int(tickmark_h*math.cos(math.radians(30*i))),cx+int(platesize*math.sin(math.radians(30*i))),cy-int(platesize*math.cos(math.radians(30*i))),tickmark_h_color)

while True:
    if Touch.Gestures == 0x03:
        showcolor()
        Touch.Gestures = 'none'
    else:watch()


