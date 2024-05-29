import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
qmi8658=touch.QMI8658()

color = LCD.color
LCD.set_bl_pwm(35535)
BG = color(0,0,0)
c1 = color(120,120,120)
c2 = color(255,255,255)

LCD.fill(BG)

def controlMotion():
    xyz0=qmi8658.Read_XYZ()
    xyz1=qmi8658.Read_XYZ()
    LCD.line(60,120+int(120*xyz0[0]),60,120+int(120*xyz1[0]),c1)
    
def block():
    
    blocksite = random.randint(-60,60)
    LCD.fill_rect(180,120+blocksite,60,60,c1)
    LCD.fill_rect(181,121+blocksite,58,58,BG)
    
def updatescreen():
    LCD.fill_rect(80,0,160,240,BG)
    LCD.scroll(-2,0)
n = 0    
while 1:
    try:
        controlMotion()
        if n % 80 == 0:block()
        updatescreen()
        LCD.show()
        n=n+1
    except KeyboardInterrupt:break
    