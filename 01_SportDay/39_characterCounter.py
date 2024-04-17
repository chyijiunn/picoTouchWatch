import touch,time,random,math
LCD = touch.LCD_1inch28()
x = 80
LCD.fill(0)
a = [8,16,24,32,40,48]

for i in range(6):
    LCD.write_text('H',x,20+35*i,i+1,LCD.white)
    LCD.line(x,20+35*i,x+a[i],20+35*i,LCD.white)
    LCD.line(x,20+35*i,x,20+35*(i+1),LCD.red)
LCD.show()
