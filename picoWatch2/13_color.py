from touch import *
LCD = LCD_1inch28()
LCD.set_bl_pwm(15535)

def color(R,G,B): #  RGB888 to RGB565
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

# https://coolors.co/generate，改一下(R,G,B)
color_1 = color(234, 149, 227)
color_2 = color(97, 201, 168)
print(color_1,color_2)

LCD.fill(color_1)
LCD.fill_rect(20,20,80,80,color_2)

for i in range(50):
    LCD.scroll(2,2)#以整個畫面為單位，每次位移 x , y 都 +2
    time.sleep(0.01)
    LCD.show()

