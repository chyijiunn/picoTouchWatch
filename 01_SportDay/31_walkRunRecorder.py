# dataCollect 第 82 行
# https://docs.google.com/spreadsheets/d/19yTWRfJCFfPKinBj__5vQDN4fPmRtZGEf7gbLsdc3IU/edit?usp=sharing

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
    LCD.fill(0)
    hourspin(cx,cy, int(spinLen*0.8) , color(R,G,B))
    spin(cx,cy, 4,spinLen,color(255,G,B))
    runDotRing(5,110,color(255,0,0))
    LCD.show()

def record(dataname,sportState):
    Touch.Gestures = 'none'#先清空Gestures值
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
        
        if xyz1[5]*xyz0[5]<0:#todo
            data.write(str(now)+','+str(round(1000*xyz1[0],3)) +','+str(1000*round(xyz1[1],3))+','+str(1000*round(xyz1[2],3))+','+str(round(xyz1[3],3))+','+str(round(xyz1[4],3))+','+str(round(xyz1[5],3))+'\n')
            dataNum = dataNum + 1
        if  Touch.Gestures == 0x04:break#滑回主畫面
    data.close()
    LCD.write_text('Finish',70,digitalystart+40,2,FC)
    LCD.show()
    return now , dataNum

def countdown(sec):
    for i in range(sec,-1,-1):
        LCD.fill(color(250-30*i,0,200-30*i))
        LCD.write_text('Ready',65,60,3,color(196, 187, 184))
        LCD.write_text(str(i),100,100,6,color(245, 176, 203))
        LCD.write_text('Jog',87,160,3,color(220, 106, 207))
        LCD.show()
        time.sleep(1)
        
def main():
    while Touch.Gestures != 0x03:watch(120,120,100)
    LCD.fill(LCD.black)
    record('datawalk.csv','WalkState')
    countdown(3)
    record('datarun.csv','RunState')

main()