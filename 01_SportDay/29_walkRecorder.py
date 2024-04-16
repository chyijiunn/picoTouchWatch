#從第 72 行開始
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
qmi8658=touch.QMI8658()

color = LCD.color
LCD.set_bl_pwm(35535)
cx , cy =120 ,120 
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))


def spin( cx,cy,tic , spinLen , color):
    now = list(time.localtime())
    x = spinLen*math.sin(math.radians(now[tic]*6))
    y = spinLen*math.cos(math.radians(now[tic]*6))
    LCD.line(cx,cy,int(cx+x),int(cy-y),color)
    
def hourspin(cx,cy,spinLen , color):
    now = list(time.localtime())
    
    if now[3] < 12:hh = now[3]
    else : hh = now[3] - 12
    
    x = spinLen*math.sin(math.radians(hh*30+(now[4]/2)))
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
                
def watch(cx,cy, spinLen):
    hourspin(cx,cy, int(spinLen*0.8) , color(R,G,B))
    spin(cx,cy, 4,spinLen,color(255,G,B))
    runDotRing(5,110,color(255,0,0))
    
def stoptime_main():
    dataNum = 1
    BG = color(R,G,B)
    FC = color(255-R,255-G,255-B)
    LCD.fill(BG)
    N1 = time.ticks_ms()
    digitalxstart = 20
    digitalystart = 100
    
    data = open('record_walk.csv','a')

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
        if xyz0[1] < -0.95 :break
        
    data.close()
    LCD.write_text('TimeUP',70,digitalystart+40,2,FC)
    LCD.show()
    
    return now , dataNum

while Touch.Gestures != 0x03:#當不是滑動到右邊時，顯示手錶時間
    LCD.fill(0)
    watch(120,120,100)
    LCD.show()
    time.sleep(0.5)

LCD.fill(LCD.black)

traindata = list(stoptime_main())

LCD.fill(LCD.black)
LCD.write_text(str(traindata[0]),60,150,2,color(90,180,40))
LCD.write_text('DataWalk = '+ str(traindata[1]),70,180,1,color(250,180,40))
LCD.show()

