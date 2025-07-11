import time , math , touch
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(15535)

def spin(value,base_length,r,c):#針底部寬度、長度、顏色
    spinBottomx_shift = int(base_length*math.sin(math.radians(value+90)))
    spinBottomy_shift = int(base_length*math.cos(math.radians(value+90)))
    spinTopX_shift = int(r*math.sin(math.radians(value)))
    spinTopY_shift = int(r*math.cos(math.radians(value)))
            
    LCD.fill_tri(cx+spinTopX_shift,cy-spinTopY_shift,cx+spinBottomx_shift,cy-spinBottomy_shift,cx-spinBottomx_shift,cy+spinBottomy_shift,c)

def watch():
    BG = color(0,0,0)
    LCD.fill(BG)
    #錶盤大小
    platesize = 40
    #錶盤中心點
    cx , cy  = 70 ,70
    #定義時、分刻度線
    tickmark_h , tick_mark_m = platesize-3 , platesize
    tickmark_h_color = color(255,100,0)
    tickmark_m_color = color(255,0,0)
    #針長度、顏色
    secspin ,minspin , hourspin = tickmark_h-5,platesize ,platesize/2
    seccolor , minspincolor , hourspincolor =color(250,225,0),color(200,100,0) ,color(250,50,125)

    for i in range(60):#分刻度線
        LCD.line(cx+int(tick_mark_m*math.sin(math.radians(6*i))),cy-int(tick_mark_m*math.cos(math.radians(6*i))),cx+int(platesize*math.sin(math.radians(6*i))),cy-int(platesize*math.cos(math.radians(6*i))),tickmark_m_color)
    for i in range(12):#時刻度線
        LCD.line(cx+int(tickmark_h*math.sin(math.radians(30*i))),cy-int(tickmark_h*math.cos(math.radians(30*i))),cx+int(platesize*math.sin(math.radians(30*i))),cy-int(platesize*math.cos(math.radians(30*i))),tickmark_h_color)

    while True:
        now = list(time.localtime())
        x_shift = int(secspin*math.sin(math.radians(6*now[5])))
        y_shift = int(secspin*math.cos(math.radians(6*now[5])))
        c = hourspincolor
        spin((30*now[3]+0.5*now[4]),4,hourspin,c)#hour
        c = minspincolor
        spin((6*now[4]+0.1*now[5]),3,minspin,c)#min
        c = seccolor
        LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)#sec
        LCD.show()
        c = BG
        spin((30*now[3]+0.5*now[4]),4,hourspin,c)
        spin((6*now[4]+0.1*now[5]),3,minspin,c)
        LCD.line(cx,cy,cx+x_shift,cy-y_shift,c)
