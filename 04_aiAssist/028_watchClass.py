import time, math
from hw import LCD
color = [
    [LCD.color(  0,  0,  0), LCD.color(220,220,220), LCD.color(160,160,160), LCD.color(255,  0,  0)],
    [LCD.color( 10, 20, 50), LCD.color( 40, 60,120), LCD.color( 90,110,160), LCD.color(255,140,  0)],
    [LCD.color( 10, 30, 20), LCD.color( 30, 80, 60), LCD.color( 70,130,110), LCD.color(220,255,  0)],
    [LCD.color( 30, 10, 40), LCD.color( 80, 40,100), LCD.color(140,100,160), LCD.color(255, 60,150)],
    [LCD.color( 40, 25, 10), LCD.color(100, 70, 40), LCD.color(170,150,110), LCD.color(220, 30, 30)],
    [LCD.color( 20, 20, 20), LCD.color( 60, 60, 60), LCD.color(150,150,150), LCD.color(  0,200,255)],
    [LCD.color(  5, 30, 35), LCD.color( 20, 80, 90), LCD.color( 60,130,160), LCD.color(255,220,  0)],
    [LCD.color( 40, 10, 15), LCD.color(120, 40, 50), LCD.color(190,120,120), LCD.color(255, 80,  0)],
    [LCD.color(  5, 15, 40), LCD.color( 30, 50,100), LCD.color( 80,110,160), LCD.color(  0,255,120)],
    [LCD.color( 25, 20, 35), LCD.color( 70, 60, 90), LCD.color(140,130,160), LCD.color(  0,220,200)],
    [LCD.color( 35, 20, 10), LCD.color( 90, 60, 30), LCD.color(190,160,120), LCD.color(255, 40, 40)],
    [LCD.color(  0,  5, 15), LCD.color( 10, 20, 40), LCD.color(120,130,150), LCD.color( 50,180,255)]
]
class Watch:
    def __init__(self, cx, cy, factor, colorSet):
        self.cx = cx
        self.cy = cy
        self.factor = factor
        self.colorSet = colorSet

    def spin(self, value, length, color):
        x = math.sin(math.radians(value * 6))
        y = math.cos(math.radians(value * 6))
        LCD.line(self.cx, self.cy,
                 int(length * x + self.cx),
                 int(-length * y + self.cy),
                 color)

    def draw(self):
        now = list(time.localtime())
        r = self.factor * 120
        h = now[3] % 12

        self.spin((now[4]/60 + h)*5, r*5/12,  color[self.colorSet][1])
        self.spin(now[4],            r*10/12, color[self.colorSet][2])
        self.spin(now[5],            r*11/12, color[self.colorSet][3])

        LCD.show()
        LCD.fill(color[self.colorSet][0])

watch = Watch(180, 180, 0.3, 7)

while True:
    watch.draw()
    time.sleep(1)
