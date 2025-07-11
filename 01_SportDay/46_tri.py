from machine import Pin,I2C,SPI,PWM
import framebuf , time , math , touch
cx , cy  = 120 ,120
LCD = touch.LCD_1inch28()
LCD.set_bl_pwm(15535)

r = 100
ti = 60
tick = 360/ ti
spinwidth = 10

c = LCD.red

for i in range(ti):    
    spinBottomLx_shift = int(spinwidth*math.sin(math.radians(i*tick+90)))
    spinBottomLy_shift = int(spinwidth*math.cos(math.radians(i*tick+90)))
    
    spinBottomRx_shift = int(spinwidth*math.sin(math.radians(i*tick-90)))
    spinBottomRy_shift = int(spinwidth*math.cos(math.radians(i*tick-90)))
    
    spinTopX_shift = int(r*math.sin(math.radians(i*tick)))
    spinTopY_shift = int(r*math.cos(math.radians(i*tick)))
        
    tri_filled(cx+spinTopX_shift,cy-spinTopY_shift,cx+spinBottomLx_shift,cy-spinBottomLy_shift,cx+spinBottomRx_shift,cy-spinBottomRy_shift,c)
    LCD.show()
    #time.sleep(1)
    LCD.fill(LCD.white)
    
    print(i)