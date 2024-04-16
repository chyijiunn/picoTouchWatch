#從第 72 行開始
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
qmi8658=touch.QMI8658()

color = LCD.color
LCD.set_bl_pwm(15535)
cx , cy =120 ,120
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

def spin( tic , spinLen , color):
    now = list(time.localtime())
    x = spinLen*math.sin(math.radians(now[tic]*6))
    y = spinLen*math.cos(math.radians(now[tic]*6))
    LCD.line(cx,cy,int(cx+x),int(cy-y),color)
    
def hourspin(spinLen , color):
    now = list(time.localtime())
    
    if now[3] < 12:hh = now[3]#切換24小時制 --> 12 小時制
    else : hh = now[3] - 12
    
    x = spinLen*math.sin(math.radians(hh*30+(now[4]/2))) #hour spin 30˚/h , +0.5˚/min
    y = spinLen*math.cos(math.radians(hh*30+(now[4]/2)))
    LCD.line(cx,cy,int(cx+x),int(cy-y),color)

def centerCircle(tic , spinLen , color):
    now = list(time.localtime())
    r = now[tic]*2
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+i,cy+j,color)
                
def runDotRing(tic , spinLen , color):
    r = 10
    now = list(time.localtime())
    x = int(spinLen*math.sin(math.radians(now[tic]*6)))
    y = int(spinLen*math.cos(math.radians(now[tic]*6)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)

def record(dataname,sportState):
    Touch.Gestures = 'none'
    dataNum = 1
    BG = color(R,G,B)
    FC = color(255-R,255-G,255-B)
    LCD.fill(BG)
    N1 = time.ticks_ms()
    digitalxstart = 20
    digitalystart = 100
    LCD.write_text(sportState,digitalxstart,digitalystart-30,3,FC)
    data = open(str(dataname),'a')

    while True:
        xyz0 = qmi8658.Read_XYZ()
        LCD.fill_rect(digitalxstart,digitalystart,210,25,BG)
        N2 = time.ticks_ms()-N1
        cS = int(N2//10)
        S = int(N2 //1000)
        M =int(S//60)
        H =int(M//60)
        now = str(H)+':'+str(M%60)+':'+str(S%60)+'.'+str(cS%100)
        LCD.write_text(now,digitalxstart,digitalystart,3,FC)
        
        LCD.show()
        xyz1 = qmi8658.Read_XYZ()
        
        if xyz1[5]*xyz0[5]<0:
            data.write(str(now)+','+str(round(1000*xyz1[0],3)) +','+str(1000*round(xyz1[1],3))+','+str(1000*round(xyz1[2],3))+','+str(round(100*(xyz1[3]-xyz0[3]),2))+','+str(round(100*(xyz1[4]-xyz0[4]),2))+','+str(round(100*(xyz1[5]-xyz0[5]),2))+'\n')
            dataNum = dataNum + 1
        if  Touch.Gestures == 0x04:break#滑回主畫面
    data.close()
    LCD.write_text('Done',90,digitalystart+40,2,FC)
    LCD.show()
    return now , dataNum

def watch():
    LCD.fill(LCD.black)
    spin(4,100,color(256-R,256-G,256-B))#分
    hourspin(50 , color(256-R,256-G,B))#時
    runDotRing(5,110,color(256-R,G,256-B))
    LCD.show()
    time.sleep(0.5)

def countdown():
    for i in range(5,-1,-1):
        LCD.fill(LCD.black)
        LCD.write_text(str(i),100,100,6,color(250,180,40))
        LCD.show()
        time.sleep(1)
    
def main():
    while Touch.Gestures != 0x03:watch()
    LCD.fill(LCD.black)
    record('datawalk.csv','WalkState')
    countdown()
    record('datarun.csv','RunState')

main()