import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch = touch.Touch_CST816T(mode=0,LCD=LCD)
color = LCD.color

def date():
    global now
    now = list(time.localtime())
    LCD.write_text(str(now[2]),120,30,3,color(255,255,255))#date
    LCD.write_text(day(),168,40,2,daycolor())#星期
    LCD.write_text('{:0>2}:'.format(now[3])+'{:0>2}'.format(now[4]),120,60,2,color(125,100,200))#digitalClock:hour,min
    LCD.write_text('{:0>2}'.format(now[5]),128,80,4,color(125,100,200))#digitalClock:sec
    LCD.show()
    LCD.fill_rect(120,20,80,100,BG)#refresh
    
def day():
    key = now[6]
    day = ['MON','TUE','WED','THU','FRI','SAT','SUN']
    return day[key]
def daycolor():
    if now[6] == 5 : daycolor = color(0,255,0)
    elif now[6] == 6 : daycolor = color(255,0,0)
    else : daycolor = color(255,255,255)
    return daycolor

LCD.set_bl_pwm(65535)
BG = color(0,0,0)
LCD.fill(BG)

while True:
    if Touch.Gestures == 0x03:
        Touch.Gestures = 'none'
    else:date()
