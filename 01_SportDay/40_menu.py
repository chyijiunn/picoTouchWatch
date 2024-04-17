from machine import ADC ,Pin
import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
Vbat_Pin = 29
color = LCD.color
LCD.set_bl_pwm(35535)
cx , cy =120 ,120 #center of watch
R,G,B = (random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))

c1 = color(R,G,B)
c2 = color(256 - R,255,100)
c3 = color(256-R,120 ,B)

def lineCharacterCount(string,charactersize):
    lenth = 8*len(string)*charactersize
    x = int(cx - lenth/2)
    return x 
    
def displayWord(word,charactersize):
    LCD.write_text(word,lineCharacterCount(word,charactersize),cy,charactersize,c1)
    
def function_1():
    while 1:
        LCD.fill(0)
        displayWord('Right',5)
        LCD.show()
        if Touch.Gestures == 0x04:break
        
def function_2():
    LCD.fill(0)
    displayWord('Left',5)
    LCD.show()
    
def function_3():
    LCD.fill(0)
    displayWord('Up',5)
    LCD.show()
    
def function_4():
    LCD.fill(0)
    displayWord('Down',5)
    LCD.show()
    
while 1:
    #功能 1，滑向右邊
    if Touch.Gestures == 0x03:
        function_1()
        Touch.Gestures = 'none'
        
    #功能 2，滑向左邊
    elif Touch.Gestures == 0x04:
        function_2()
        Touch.Gestures = 'none'
    #功能 3 ，滑向上面
    elif Touch.Gestures == 0x02:
        Touch.Gestures = 'none'#先清空Gestures值
        function_3()
        Touch.Gestures = 'none'#若沒清空Gestures值，回刷時會因為功能 4 多功能錶盤而進入功能4
    #功能 4 ，滑向下面
    elif Touch.Gestures == 0x01:
        Touch.Gestures = 'none'
        function_4()
        Touch.Gestures = 'none'

    else:
        LCD.fill(0)
        displayWord('Main',4)
        LCD.show()
        