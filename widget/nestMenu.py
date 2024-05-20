# 儘量避免使用巢狀menu
# line 33 必要使用時，需搭配長按、避免連續同方向之撥選
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
    
def function_B1():#0x01 下
    Touch.Gestures = 'none'
    time.sleep(1)
    while 1:
        LCD.fill(c3)
        displayWord('B1F',5)
        LCD.show()
        if Touch.Gestures == 0x02:break
        if Touch.Gestures == 0x01:function_B2()#需要換成長按 0x0c 或其他方向

def function_B2():
    Touch.Gestures = 'none'
    while 1:
        LCD.fill(c2)
        displayWord('B2F',4)
        LCD.show()
        if Touch.Gestures == 0x02:break# return to function1
        
def function_2F():#0x02 上
    LCD.fill(0)
    displayWord('2F',5)
    LCD.show()
    
def function_R():#0x03 右
    LCD.fill(0)
    displayWord('R1',5)
    LCD.show()
    
def function_L():#0x04 左
    LCD.fill(0)
    displayWord('L1',5)
    LCD.show()
    
while 1:
    #功能 1，滑向下
    if Touch.Gestures == 0x01:
        function_B1()
        Touch.Gestures = 'none'#若沒清空Gestures值，回刷時會因為向上功能，進入功能向上
    #功能 2，滑向上    
    elif Touch.Gestures == 0x02:
        function_2F()
        Touch.Gestures = 'none'
        
    #功能 3，滑向右
    elif Touch.Gestures == 0x03:
        function_R()
        Touch.Gestures = 'none'
        
    #功能 4，滑向左
    elif Touch.Gestures == 0x04:
        function_L()
        Touch.Gestures = 'none'

    else:
        LCD.fill(0)
        displayWord('Main',5)
        LCD.show()
        