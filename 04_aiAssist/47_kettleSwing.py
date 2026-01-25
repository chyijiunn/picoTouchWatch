import time , touch, math , random
LCD = touch.LCD_1inch28()
qmi8658=touch.QMI8658()
LCD.set_bl_pwm(35535)
color = LCD.color
c1 = color(255,255,255)
c2 = color(255,0,0)
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
    #draw Dot , line , or rect
    #LCD.pixel(200,ydot,c2)
    LCD.line(200,140,200,ydot,c2)
    #LCD.fill_rect(200,ydot,1,15,c2)
    
def count():
    global xyz0 , xyz1,Num
    if  (ydot < threshold):
        Num = Num+1
        time.sleep(0.5)
    LCD.fill_rect(110,200,48,24,0)
    LCD.write_text(str(Num),110,200,3,c1)
    #print(xyz0[4]*xyz1[4])

while 1:
    try:
        xyz0 = qmi8658.Read_XYZ()
        ydot = int(140 + 80*xyz0[0])
        print(ydot)
        boundary()
        drawData()
        LCD.show()
        xyz1 = qmi8658.Read_XYZ()
        count()
        
    except KeyboardInterrupt:
        break
