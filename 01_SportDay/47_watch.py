import time , math , touch
LCD = touch.LCD_1inch28()
color = LCD.color
cx , cy  = 120 ,120
LCD.set_bl_pwm(15535)
BG = color(0,0,0)
LCD.fill(BG)

def spin(value,base_length,r,c):
    spinBottomx_shift = int(base_length*math.sin(math.radians(value+90)))
    spinBottomy_shift = int(base_length*math.cos(math.radians(value+90)))
    spinTopX_shift = int(r*math.sin(math.radians(value)))
    spinTopY_shift = int(r*math.cos(math.radians(value)))     
    LCD.fill_tri(cx+spinTopX_shift,cy-spinTopY_shift,cx+spinBottomx_shift,cy-spinBottomy_shift,cx-spinBottomx_shift,cy+spinBottomy_shift,c)
    
for i in range(60):
    LCD.line(cx+int(115*math.sin(math.radians(6*i))),cy-int(115*math.cos(math.radians(6*i))),cx+int(120*math.sin(math.radians(6*i))),cy-int(120*math.cos(math.radians(6*i))),color(255,0,0))
for i in range(12):
    LCD.line(cx+int(110*math.sin(math.radians(30*i))),cy-int(110*math.cos(math.radians(30*i))),cx+int(120*math.sin(math.radians(30*i))),cy-int(120*math.cos(math.radians(30*i))),color(255,100,0))

while True:
    now = list(time.localtime())
    x_shift = int(110*math.sin(math.radians(6*now[5])))
    y_shift = int(110*math.cos(math.radians(6*now[5])))
    c = color(250,50,125)
    spin((30*now[3]+0.5*now[4]),8,60,c)#hour
    c = color(200,100,0)
    spin((6*now[4]+0.1*now[5]),7,115,c)#min
    c = color(255,225,0)
    LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)#sec
    LCD.show()
    c = color(0,0,0)#clear stage
    spin((30*now[3]+0.5*now[4]),8,60,c)
    spin((6*now[4]+0.1*now[5]),7,115,c)
    LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)
