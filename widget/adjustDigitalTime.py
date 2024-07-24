import touch,time,random,math
LCD = touch.LCD_1inch28()
Touch = touch.Touch_CST816T(mode=1,LCD=LCD)
color = LCD.color

LCD.set_bl_pwm(15535)
c1 = color(55,25,125)
c2 = color(255,225,255)
LCD.fill(0)

def triUP(tri_cx,tri_cy,tri_scale,color):
    p1x, p1y = tri_cx, tri_cy - tri_scale
    p2x, p2y = tri_cx - tri_scale ,tri_cy + tri_scale
    p3x, p3y = tri_cx + tri_scale,tri_cy + tri_scale
    LCD.fill_tri(p1x,p1y,p2x,p2y,p3x,p3y,color)
    
def triDW(tri_cx,tri_cy,tri_scale,color):
    p1x, p1y = tri_cx, tri_cy + tri_scale
    p2x, p2y = tri_cx - tri_scale ,tri_cy - tri_scale
    p3x, p3y = tri_cx + tri_scale,tri_cy - tri_scale
    LCD.fill_tri(p1x,p1y,p2x,p2y,p3x,p3y,color)
    
def touchPoint(x,y,r):
    return x-r,x+r,y-r,y+r 
    
for i in range(2):
    shift = i*100
    triUP(70+shift,60,10,0x07E0)
for i in range(2):
    shift = i*100
    triDW(70+shift,160,10,0x07E0)
    
Touch.Flag = 0
now = list(time.localtime())
LCD.write_text(str(now[3])+':'+str(now[4]),60,100,3,LCD.white)
adjustH = now[3]
adjustM = now[4]
LCD.show()
def adjust():
    global adjustH ,adjustM
    if Touch.Flag == 1:
        x = Touch.X_point
        y = Touch.Y_point
        Touch.Flag = 0
        if x > 60  and x < 80 and y > 50 and y < 70 :adjustH = adjustH +1
        elif x > 60  and x < 80 and y > 150 and y < 170 :adjustH = adjustH -1
        elif x > 160  and x < 180 and y > 50 and y < 70 :adjustM = adjustM +1
        elif x > 160  and x < 180 and y > 150 and y < 170 :adjustM = adjustM -1
        else:pass
        time.sleep(0.1)
        return str(adjustH % 24) +':'+str(adjustM % 60)
    else:return str(adjustH) +':'+str(adjustM)

    
while 1:
    LCD.write_text(str(adjust()),60,100,3,LCD.white)
    LCD.show()
    LCD.fill_rect(60,100,120,40,LCD.black)


