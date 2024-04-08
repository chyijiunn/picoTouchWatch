# PicoPong.py: a simple Pong game by Vincent Mistler (YouMakeTech)
# 引用別人寫好的乒乓來測試，若要旋轉表盤來移動，應該修改成什麼？往下到 41th line
import random , touch , machine ,time

LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(10000)
qmi8658=touch.QMI8658()
Vbat= machine.ADC(machine.Pin(29))

def color(R,G,B):
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

R = random.randint(-1,256)
G = random.randint(-1,256)
B = random.randint(-1,256)

c1 = color(R,G,B)
c2 = color(256 - R,256-G,256-B)
c3 = color(256-R,256 - G,B)

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
        xyz=qmi8658.Read_XYZ()
        #利用 xw 加速度，改成 zw 會變成？ 
        x_shift = int(xyz[3]/10)
        if x_shift < 0:
            paddleX += paddleVX
            if paddleX + PADDLE_WIDTH > SCREEN_WIDTH:
                paddleX = SCREEN_WIDTH - PADDLE_WIDTH
        elif x_shift > 0:
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
        
if __name__ == "__main__":
    pico_pong_main()