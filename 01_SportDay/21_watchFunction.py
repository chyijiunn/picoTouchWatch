import time , touch, math , random
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

def spin( cx,cy, tic , spinLen , color):
    now = list(time.localtime())
    x = spinLen*math.sin(math.radians(now[tic]*6))
    y = spinLen*math.cos(math.radians(now[tic]*6))
    LCD.line(cx,cy,int(cx+x),int(cy-y),color)
    
def hourspin(cx, cy, spinLen , color):
    now = list(time.localtime())
    
    if now[3] < 12:hh = now[3]
    else : hh = now[3] - 12
    
    x = spinLen*math.sin(math.radians(hh*30+(now[4]/2)))
    y = spinLen*math.cos(math.radians(hh*30+(now[4]/2)))
    LCD.line(cx,cy,int(cx+x),int(cy-y),color)

def centerCircle(cx,cy, tic , spinLen , color):
    now = list(time.localtime())
    r = now[tic]*2
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+i,cy+j,color)
                
def runDotRing(cx,cy, tic , spinLen , color):
    r = 10
    now = list(time.localtime())
    x = int(spinLen*math.sin(math.radians(now[tic]*6)))
    y = int(spinLen*math.cos(math.radians(now[tic]*6)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
                
def color(R,G,B):
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

def watch(cx,cy, spinLen):
    hourspin(cx,cy, spinLen-10 , color(R,G,B))#時
    spin(cx,cy, 4,spinLen,color(255,G,B))#分
      
R = random.randint(0,256)
G = random.randint(0,256)
B = random.randint(0,256)
print(R,G,B)

while 1:
    watch(60,60,25)
    watch(120,40,40)
    runDotRing(120,120, 5,110,color(R,G,B))#秒
    LCD.show()
    LCD.fill(color(255-R,255-G,255-B))
