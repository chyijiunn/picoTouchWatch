import utime , touch, math , random,sys
LCD = touch.LCD_1inch28()
qmi8658=touch.QMI8658()
LCD.set_bl_pwm(35535)
color = LCD.color
c1 = color(255,255,255)
c2 = color(255,0,0)
c3 = color(255,255,0)
LCD.fill(0)
threshold = 70
s = 0
n=0
Num = 0

def boundary():
    global n 
    if n%6 == 0:LCD.pixel(200,200,c1)
    if n%6 == 3:LCD.pixel(200,threshold,c1)
    n = n + 1
    LCD.scroll(-1,0)
    
def drawData():
    LCD.line(200,140,200,ydot,c2)
    
def count():
    LCD.fill_rect(110,200,65,24,0)
    LCD.write_text(str(ydot),110,200,3,c1)

def goal():       
    #分數
    scoreMax = max(scorelist)
    LCD.fill(0)
    average = int(100*sum(scorelist)/10/scoreMax)
    LCD.line(20,140-average,200,140-average,c3)
    for i in range(10):
        LCD.fill_rect(20 + i* 20,140-int(100*scorelist[i]/scoreMax),10,int(100*scorelist[i]/scoreMax),c2)
    #總分
    LCD.write_text(str(int(sum(scorelist))),80,160,2,c1)
    LCD.show()
    utime.sleep(3)
        
def energy():
    global s
    if xyz1[0] < xyz0[0]:
        score = (xyz1[0]-xyz0[0])*(xyz1[0]-xyz0[0])*(tick1-tick0)*pow(10,1)
        s = s+ score
        
def main():
    global ydot , xyz0 , xyz1, tick1,tick0,scorelist
    scorelist = []
    while 1:
        tick0 = utime.ticks_ms()
        xyz0 = qmi8658.Read_XYZ()
        ydot = int(140 + 85*xyz0[0])
        
        boundary()
        drawData()
        LCD.show()
        tick1 = utime.ticks_ms()
        xyz1 = qmi8658.Read_XYZ()
        count()
        
def restart():
    global Num ,s
    main()
    Num = 0
    s = 0
    
while 1:
    try:restart()
    except KeyboardInterrupt:break

