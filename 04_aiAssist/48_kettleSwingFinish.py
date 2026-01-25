import time , touch, math , random,sys
LCD = touch.LCD_1inch28()
qmi8658=touch.QMI8658()
LCD.set_bl_pwm(35535)
color = LCD.color
c1 = color(255,255,255)
c2 = color(255,0,0)
c3 = color(255,255,0)
LCD.fill(0)
threshold = 80

n=0
Num = 0

def boundary():
    global n 
    if n%6 == 0:LCD.pixel(200,180,c1)
    if n%6 == 3:LCD.pixel(200,threshold,c1)
    n = n + 1
    LCD.scroll(-1,0)
    
def drawData():
    LCD.line(200,140,200,ydot,c2)
    
def count():
    global xyz0 , xyz1,Num
    if  (ydot < threshold):
        Num = Num+1
        time.sleep(0.5)
    LCD.fill_rect(110,200,48,24,0)
    LCD.write_text(str(Num),110,200,3,c1)

def goal():
    LCD.fill(0)
    LCD.write_text('GOAL',50,180,5,c1)
    LCD.show()
    for j in range(2):
        for i in range(30):
            LCD.scroll(0,-5)
            LCD.show()
        for i in range(30):
            LCD.scroll(0,5)
            LCD.show()
    for i in range(15):
        LCD.scroll(0,-5)
        LCD.show()
    for i in range(3):
        LCD.fill(0)
        LCD.show()
        time.sleep(0.5)
        LCD.write_text('Ready',30,120,5,c1)
        LCD.show()
        time.sleep(0.5)
    for i in range(25):
        LCD.fill_rect(220,70+3*i,2,120-5*i,c3)
        LCD.scroll(-8,0)
        LCD.show()    
    
def main():
    global ydot
    while 1:
        xyz0 = qmi8658.Read_XYZ()
        ydot = int(140 + 80*xyz0[0])
        print(ydot)
        boundary()
        drawData()
        LCD.show()
        xyz1 = qmi8658.Read_XYZ()
        count()
            
        if Num > 3:
            goal()
            time.sleep(1)
            break
def restart():
    global Num
    main()
    Num = 0
    
while 1:
    try:restart()
    except KeyboardInterrupt:break
