from machine import Pin,I2C,SPI,PWM
import framebuf , time , math ,touch

LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
BG = color(0,0,0)
LCD.fill(BG)
'''
for i in range(0,255,10):
    for j in range(0,255,10):
        LCD.fill_rect(i,j,10,10,color(j,i,125))'''
        
for i in range(255):
    for j in range(255):
        LCD.pixel(i,j,color(i,j,125))
    LCD.show()