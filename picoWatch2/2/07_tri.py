from machine import Pin,I2C,SPI,PWM
import framebuf , time , math

DC = 8
CS = 9
SCK = 10
MOSI = 11
RST = 12
BL = 25
Vbat_Pin = 29

width = 240
height = 240

class LCD_1inch28(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 240
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1,100_000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff
        
        self.fill(self.white)
        self.show()

        self.pwm = PWM(Pin(BL))
        self.pwm.freq(5000)
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)
        
    def set_bl_pwm(self,duty):
        self.pwm.duty_u16(duty)#max 65535
        
    def init_display(self):
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        time.sleep(0.05)
        
        self.write_cmd(0xEF)
        self.write_cmd(0xEB)
        self.write_data(0x14) 
        
        self.write_cmd(0xFE) 
        self.write_cmd(0xEF) 

        self.write_cmd(0xEB)
        self.write_data(0x14) 

        self.write_cmd(0x84)
        self.write_data(0x40) 

        self.write_cmd(0x85)
        self.write_data(0xFF) 

        self.write_cmd(0x86)
        self.write_data(0xFF) 

        self.write_cmd(0x87)
        self.write_data(0xFF)

        self.write_cmd(0x88)
        self.write_data(0x0A)

        self.write_cmd(0x89)
        self.write_data(0x21) 

        self.write_cmd(0x8A)
        self.write_data(0x00) 

        self.write_cmd(0x8B)
        self.write_data(0x80) 

        self.write_cmd(0x8C)
        self.write_data(0x01) 

        self.write_cmd(0x8D)
        self.write_data(0x01) 

        self.write_cmd(0x8E)
        self.write_data(0xFF) 

        self.write_cmd(0x8F)
        self.write_data(0xFF) 


        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x20)

        self.write_cmd(0x36)
        self.write_data(0x98)

        self.write_cmd(0x3A)
        self.write_data(0x05) 

        self.write_cmd(0x90)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x08) 

        self.write_cmd(0xBD)
        self.write_data(0x06)
        
        self.write_cmd(0xBC)
        self.write_data(0x00)

        self.write_cmd(0xFF)
        self.write_data(0x60)
        self.write_data(0x01)
        self.write_data(0x04)

        self.write_cmd(0xC3)
        self.write_data(0x13)
        self.write_cmd(0xC4)
        self.write_data(0x13)

        self.write_cmd(0xC9)
        self.write_data(0x22)

        self.write_cmd(0xBE)
        self.write_data(0x11) 

        self.write_cmd(0xE1)
        self.write_data(0x10)
        self.write_data(0x0E)

        self.write_cmd(0xDF)
        self.write_data(0x21)
        self.write_data(0x0c)
        self.write_data(0x02)

        self.write_cmd(0xF0)   
        self.write_data(0x45)
        self.write_data(0x09)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x26)
        self.write_data(0x2A)

        self.write_cmd(0xF1)    
        self.write_data(0x43)
        self.write_data(0x70)
        self.write_data(0x72)
        self.write_data(0x36)
        self.write_data(0x37)  
        self.write_data(0x6F)

        self.write_cmd(0xF2)   
        self.write_data(0x45)
        self.write_data(0x09)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x26)
        self.write_data(0x2A)

        self.write_cmd(0xF3)   
        self.write_data(0x43)
        self.write_data(0x70)
        self.write_data(0x72)
        self.write_data(0x36)
        self.write_data(0x37) 
        self.write_data(0x6F)

        self.write_cmd(0xED)
        self.write_data(0x1B) 
        self.write_data(0x0B) 

        self.write_cmd(0xAE)
        self.write_data(0x77)
        
        self.write_cmd(0xCD)
        self.write_data(0x63)


        self.write_cmd(0x70)
        self.write_data(0x07)
        self.write_data(0x07)
        self.write_data(0x04)
        self.write_data(0x0E) 
        self.write_data(0x0F) 
        self.write_data(0x09)
        self.write_data(0x07)
        self.write_data(0x08)
        self.write_data(0x03)

        self.write_cmd(0xE8)
        self.write_data(0x34)

        self.write_cmd(0x62)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x71)
        self.write_data(0xED)
        self.write_data(0x70) 
        self.write_data(0x70)
        self.write_data(0x18)
        self.write_data(0x0F)
        self.write_data(0x71)
        self.write_data(0xEF)
        self.write_data(0x70) 
        self.write_data(0x70)

        self.write_cmd(0x63)
        self.write_data(0x18)
        self.write_data(0x11)
        self.write_data(0x71)
        self.write_data(0xF1)
        self.write_data(0x70) 
        self.write_data(0x70)
        self.write_data(0x18)
        self.write_data(0x13)
        self.write_data(0x71)
        self.write_data(0xF3)
        self.write_data(0x70) 
        self.write_data(0x70)

        self.write_cmd(0x64)
        self.write_data(0x28)
        self.write_data(0x29)
        self.write_data(0xF1)
        self.write_data(0x01)
        self.write_data(0xF1)
        self.write_data(0x00)
        self.write_data(0x07)

        self.write_cmd(0x66)
        self.write_data(0x3C)
        self.write_data(0x00)
        self.write_data(0xCD)
        self.write_data(0x67)
        self.write_data(0x45)
        self.write_data(0x45)
        self.write_data(0x10)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)

        self.write_cmd(0x67)
        self.write_data(0x00)
        self.write_data(0x3C)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x54)
        self.write_data(0x10)
        self.write_data(0x32)
        self.write_data(0x98)

        self.write_cmd(0x74)
        self.write_data(0x10)
        self.write_data(0x85)
        self.write_data(0x80)
        self.write_data(0x00) 
        self.write_data(0x00) 
        self.write_data(0x4E)
        self.write_data(0x00)
        
        self.write_cmd(0x98)
        self.write_data(0x3e)
        self.write_data(0x07)

        self.write_cmd(0x35)
        self.write_cmd(0x21)

        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x29)
        time.sleep(0.02)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

class Point:
    def __init__(self,x,y):
        self.X=x
        self.Y=y
    def __str__(self):
        return "Point(%s,%s)"%(self.X,self.Y)
        
class Triangle:
    def __init__(self,p1,p2,p3):
        self.P1=p1
        self.P2=p2
        self.P3=p3

    def __str__(self):
        return "Triangle(%s,%s,%s)"%(self.P1,self.P2,self.P3)
    
    def draw(self):
        print("I should draw now")
        self.fillTri()
      
    def sortVerticesAscendingByY(self):    
        if self.P1.Y > self.P2.Y:
            vTmp = self.P1
            self.P1 = self.P2
            self.P2 = vTmp
        
        if self.P1.Y > self.P3.Y:
            vTmp = self.P1
            self.P1 = self.P3
            self.P3 = vTmp

        if self.P2.Y > self.P3.Y:
            vTmp = self.P2
            self.P2 = self.P3
            self.P3 = vTmp
        
    def fillTri(self):
        self.sortVerticesAscendingByY()
        if self.P2.Y == self.P3.Y:
            fillBottomFlatTriangle(self.P1, self.P2, self.P3)
        else:
            if self.P1.Y == self.P2.Y:
                fillTopFlatTriangle(self.P1, self.P2, self.P3)
            else:
                newx = int(self.P1.X + (float(self.P2.Y - self.P1.Y) / float(self.P3.Y - self.P1.Y)) * (self.P3.X - self.P1.X))
                newy = self.P2.Y                
                pTmp = Point( newx,newy )
                fillBottomFlatTriangle(self.P1, self.P2, pTmp)
                fillTopFlatTriangle(self.P2, pTmp, self.P3)

def fillBottomFlatTriangle(p1,p2,p3):
    if p2.Y > p3.Y:
        ty = p3.Y
        p3.Y = p2.Y
        p2.Y = ty
        tx = p3.X
        p3.X = p2.X
        p2.X = tx
        print(p1,p2,p3)
    
    slope1 = float(p2.X - p1.X) / float (p2.Y - p1.Y)
    slope2 = float(p3.X - p1.X) / float (p3.Y - p1.Y)

    x1 = p1.X
    x2 = p1.X + 0.5

    for scanlineY in range(p1.Y,p2.Y):
        LCD.hline(int(x1),scanlineY, int(x2)-int(x1),c)        
        LCD.hline(int(x2),scanlineY, -(int(x2)-int(x1)),c)

        x1 += slope1
        x2 += slope2

def fillTopFlatTriangle(p1,p2,p3):
    slope1 = float(p3.X - p1.X) / float(p3.Y - p1.Y)
    slope2 = float(p3.X - p2.X) / float(p3.Y - p2.Y)
    x1 = p3.X
    x2 = p3.X + 0.5

    for scanlineY in range (p3.Y,p1.Y-1,-1):
        LCD.hline(int(x1),scanlineY, int(x2)-int(x1)+1,c)        
        LCD.hline(int(x2),scanlineY, -(int(x2)-int(x1)-1),c)
        x1 -= slope1
        x2 -= slope2

def triangle(x1,y1,x2,y2,x3,y3,c): 
    LCD.line(x1,y1,x2,y2,c)
    LCD.line(x2,y2,x3,y3,c)
    LCD.line(x3,y3,x1,y1,c)
    
def tri_filled(x1,y1,x2,y2,x3,y3,c): 
    t=Triangle(Point(x1,y1),Point(x2,y2),Point(x3,y3))
    t.fillTri() 

def end_point(theta, rr): # Calculate end of hand offsets
    theta_rad = math.radians(theta)                       
    theta_rad = math.radians(theta)    
    xx = int(rr * math.sin(theta_rad))
    yy = -int(rr * math.cos(theta_rad))                     
    return xx,yy

cx , cy  = 120 ,120
LCD = LCD_1inch28()
LCD.set_bl_pwm(5535)
c = LCD.red
r = 60

ti = 20
tick = 360/ ti
for i in range(ti):
    x_shift = int(r*math.sin(math.radians(i*tick)))
    y_shift = int(r*math.cos(math.radians(i*tick)))
        
    x_shift_next = int(r*math.sin(math.radians(tick*(i+1))))
    y_shift_next = int(r*math.cos(math.radians(tick*(i+1))))
        
    tri_filled(cx,cy,cx+x_shift,cy-y_shift,cx+x_shift_next,cy-r*y_shift_next,c)
    LCD.show()
    #LCD.fill(LCD.white)
    
    print(i)

