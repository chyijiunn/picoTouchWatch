import touch,time
LCD = touch.LCD_1inch28()
color = LCD.color
xyz = touch.QMI8658().Read_XYZ()
Touch=touch.Touch_CST816T(mode=0,LCD=LCD)
LCD.set_bl_pwm(35535)

LCD.fill(LCD.white)
LCD.write_text('Trunking',60,25,2,color(90,180,40))

for i in range(0,3):
    LCD.write_text(str('{:>.2f}'.format(xyz[i])),60,125+8*i,1,color(90,180,40))
for i in range(3,6):
    LCD.write_text(str('{:>.2f}'.format(xyz[i])),60,125+8*i,1,color(90,180,200))

LCD.show()

time.sleep(1)

while Touch.Gestures != 0x01:
    LCD.fill(LCD.black)
    LCD.write_text('UP',100,125,3,color(90,180,200))
    LCD.show()

LCD.fill(LCD.black)
LCD.write_text('Great',70,125,3,color(90,180,200))
LCD.show()