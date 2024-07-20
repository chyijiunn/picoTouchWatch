import time , touch, math , random
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)
color = LCD.color

def watch():
    cx , cy =120 ,120 #center of watch
    def spin( tic , spinLen , color):
        now = list(time.localtime())
        x = spinLen*math.sin(math.radians(now[tic]*6))
        y = spinLen*math.cos(math.radians(now[tic]*6))
        LCD.line(cx,cy,int(cx+x),int(cy-y),color)
        
    def hourspin(spinLen , color):
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
    spin(4,100,color(256-R,256-G,256-B))#分
    hourspin(50 , color(256-R,256-G,B))#時
    runDotRing(5,110,color(256-R,G,256-B))

R = random.randint(0,256)
G = random.randint(0,256)
B = random.randint(0,256)

while 1:
    watch()
    LCD.show()
    LCD.fill(0)
