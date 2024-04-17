import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
color = LCD.color
LCD.set_bl_pwm(35535)

R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))
c1 = color(R,G,B)
    
def function():
    while 1:
        LCD.fill(0)
        LCD.write_text('Right',40,100,5,c1)
        LCD.show()
        if Touch.Gestures == 0x04:break
    
while 1:
    #功能 1，滑向右邊
    if Touch.Gestures == 0x03:
        function()
        #Touch.Gestures = 'none'

    else:
        LCD.fill(0)
        LCD.write_text('Main',50,100,5,c1)
        LCD.show()