import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(35535)
'''
BG = color(0,0,0)
LCD.fill(BG)
for i in range(255):
    for j in range(255):
        LCD.pixel(i,j,color(i,j,125))        
        
LCD.show()
'''
while 1:
    print(Touch.get_point)
    time.sleep(1)