from touch import *
import Module.tri as Geometry

cx , cy  = 120 ,120
r = 60

LCD = LCD_1inch28()
LCD.set_bl_pwm(5535)
c = LCD.red

Geometry.Triangle.triangle(cx,cy,cx+r,cy+r,cx-r,cy+r,c)

LCD.line(120,120,40,80,c)
LCD.show()

