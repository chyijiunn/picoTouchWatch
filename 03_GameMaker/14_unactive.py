#新增 list ，超過某數量刪除前面紀錄點
from machine import Pin, PWM
from utime import sleep
import touch , _thread
LCD = touch.LCD_1inch28()
color = LCD.color
LCD.set_bl_pwm(35535)
Touch=touch.Touch_CST816T(mode=1,LCD=LCD)
Touch.tim.init(period=1, callback=Touch.Timer_callback)
Touch.Flag = False
LCD.fill(color(0,0,0))
position = []

class Laser:
    def __init__(self, width, height):
        # initialize laser starting coordinates
        # from ship coordinates
        self.width = width
        self.height = height
        self.x = -1         # laser position on screen
        self.y = -1
        '''
        self.x0 = -1        # ship position when firing
        self.y0 = -1
        '''
        self.active = False # True whe a laser is displayed
        self.released = False   # True once right after firing
        
    def fire(self, x0, y0):
        if not self.active:
            self.x0 = x0
            self.y0 = y0
            self.x = x0 + 5
            self.y = y0
            self.active = True
        
    def move(self, vy):
        if self.active:
            self.y += vy
            if self.y < 0:
                self.active = False
            
    def draw(self, LCD):
        if self.active:
            LCD.fill_rect(int(self.x), int(self.y), self.width, self.height, color(255,255,0))   
LASER_WIDTH = 2
LASER_HEIGHT = 5
laser = Laser(LASER_WIDTH, LASER_HEIGHT)

while 1:
    if Touch.Flag == True:
        x , y = Touch.X_point , Touch.Y_point
        laser.fire(x,y)
        laser.move(-5)
        laser.draw(LCD)
        LCD.show()
        Touch.Flag = False
        sleep(0.05)
 




