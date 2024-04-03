import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)

color = LCD.color
LCD.set_bl_pwm(35535)
cx , cy =120 ,120 #center of watch
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

c1 = color(R,G,B)
c2 = color(256 - R,256-G,256-B)
c3 = color(256-R,256 - G,B)

walknum = 0
walkTARGET = 100 # 每天要走幾步
runnum = 0
runTARGET = 100 # 每天要跑幾步
threhold = 300 #設立閾值

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

def stoptime():
    BG = color(R,G,B)
    FC = color(255-R,255-G,255-B)
    LCD.fill(BG)
    N1 = time.ticks_ms()#Start 時刻
    digitalxstart = 20
    digitalystart = 100

    while True:
        LCD.fill_rect(digitalxstart,digitalystart,210,25,BG)#數字refresh
        xyz = touch.QMI8658().Read_XYZ()
        N2 = time.ticks_ms()-N1#End 時刻
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
    return now

def watch():
    LCD.fill(LCD.black)
    spin(4,100,color(R,G,B))#分
    hourspin(50 , color(255,255-G,B))#時
    runDotRing(5,110,color(255,0,0))
    LCD.show()
    time.sleep(0.5)
    
def pico_pong_main():
    SCREEN_WIDTH = 240                       
    SCREEN_HEIGHT = 240
    BALL_SIZE = int(SCREEN_WIDTH/32)         
    PADDLE_WIDTH = int(SCREEN_WIDTH/8)       
    PADDLE_HEIGHT = int(SCREEN_HEIGHT/16)
    PADDLE_Y = SCREEN_HEIGHT-2*PADDLE_HEIGHT

    ballX = random.randint(0,240)    
    ballY = 120
    ballVX = 2.0    
    ballVY = 2.0 

    paddleX = int(SCREEN_WIDTH/2) 
    paddleVX = 3  
    score = 0

    while True:
        #讀取xyz
        xyz=touch.QMI8658().Read_XYZ()
        x_shift = int(xyz[1]*10)
        if x_shift > 0:
            paddleX += paddleVX
            if paddleX + PADDLE_WIDTH > SCREEN_WIDTH:
                paddleX = SCREEN_WIDTH - PADDLE_WIDTH
        elif x_shift < 0:
            paddleX -= paddleVX
            if paddleX < 0:
                paddleX = 0
        if abs(ballVX) < 1:
            ballVX = 1

        ballX = int(ballX + ballVX)
        ballY = int(ballY + ballVY)

        collision=False
        if ballX < 0:
            ballX = 0
            ballVX = -ballVX
            collision = True
        
        if ballX + BALL_SIZE > SCREEN_WIDTH:

            ballX = SCREEN_WIDTH-BALL_SIZE
            ballVX = -ballVX
            collision = True

        if ballY+BALL_SIZE>PADDLE_Y and ballX > paddleX-BALL_SIZE and ballX<paddleX+PADDLE_WIDTH+BALL_SIZE:
            ballVY = -ballVY
            ballY = PADDLE_Y-BALL_SIZE
            ballVY -= 0.2
            ballVX += (ballX - (paddleX + PADDLE_WIDTH/2))/10
            collision = True
            score += 10
            
        if ballY < 0:
            ballY = 0
            ballVY = -ballVY
            collision = True
            
        if ballY + BALL_SIZE > SCREEN_HEIGHT:
            LCD.fill(c1)
            LCD.text("GAME OVER", int(SCREEN_WIDTH/2)-int(len("Game Over!")/2 * 8), int(SCREEN_HEIGHT/2) - 8,LCD.white)
            LCD.text(str(score),int(SCREEN_WIDTH/2)-int(len(str(score))/4),int(SCREEN_HEIGHT/10),LCD.white)
            LCD.show()
            
            while x_shift == 0 :
                time.sleep(0.001)
            break
            
        LCD.fill(c1)
        LCD.fill_rect(paddleX, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, c2)
        LCD.fill_rect(ballX, ballY, BALL_SIZE, BALL_SIZE, c3)
        LCD.text(str(score), int(SCREEN_WIDTH/2)-int(len(str(score))*8),int(SCREEN_HEIGHT/10),LCD.white)
        LCD.show()
        
def runDotRingAdvanced(r , walkreach , spinLen , color):
    x = int(spinLen*math.sin(math.radians(walkreach*360)))
    y = int(spinLen*math.cos(math.radians(walkreach*360)))
    for i in range(-r,r,1):
        for j in range(-r,r,1):
            if i*i + j*j <= r*r:
                LCD.pixel(cx+x+i,cy-y+j,color)
                
def walkandRun():
    global walknum , runnum
    while Touch.Gestures != 0x01:
        xyz=touch.QMI8658().Read_XYZ()
        N1 = xyz[5]
        time.sleep(0.05)
        xyz=touch.QMI8658().Read_XYZ()
        N2 = xyz[5]
        y = xyz[1]
        if N1*N2 < 0:#這裡以個人的資料來定義
            if (N1>10 and N1<threhold) or (N2>10 and N2<threhold):
                walknum = walknum + 1
            elif (((N1 or N2) > threhold) or ((N1 or N2)< -threhold)) and y < - 0.8:
                runnum = runnum + 1
        walkreach = walknum/walkTARGET
        runreach = runnum/runTARGET
        
        runDotRingAdvanced(12,walkreach,110,color(walknum,180,walknum))#走路外圈，點繞行
        runDotRingAdvanced(12,runreach,88,color(runnum,180,180))#跑步內圈資料
        
        LCD.write_text(str(walknum),90,120,3,color(int(walkreach*128),180,int(walkreach*128)))
        #LCD.write_text(str(int(runreach*100))+'%'+str(runnum),90,100,3,color(int(runreach*128),180,180))
        
        LCD.show()
        LCD.fill_rect(80,100,100,50,LCD.black)
    
while 1:
    #功能 1 碼錶，滑向右邊錶盤
    if Touch.Gestures == 0x03:
        stoptime()
        Touch.Gestures = 'none'
        
    #功能 2 小遊戲，滑向左邊錶盤
    elif Touch.Gestures == 0x04:
        pico_pong_main()
        Touch.Gestures = 'none'
    #功能 3 計步器，滑向上面錶盤
    elif Touch.Gestures == 0x02:
        Touch.Gestures = 'none'
        LCD.fill(LCD.black)
        LCD.show()
        walkandRun()

    else:watch()
