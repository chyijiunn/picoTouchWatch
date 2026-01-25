import time, math
from hw import LCD

LCD.fill(0)
cx ,cy =180,180
color = [
    # 0. 深黑背景｜經典白灰紅
    [LCD.color(  0,  0,  0), LCD.color(220,220,220), LCD.color(160,160,160), LCD.color(255,  0,  0)],

    # 1. 深藍背景｜藍系 × 亮橘
    [LCD.color( 10, 20, 50), LCD.color( 40, 60,120), LCD.color( 90,110,160), LCD.color(255,140,  0)],

    # 2. 深墨綠背景｜綠系 × 螢光黃
    [LCD.color( 10, 30, 20), LCD.color( 30, 80, 60), LCD.color( 70,130,110), LCD.color(220,255,  0)],

    # 3. 深紫背景｜紫系 × 桃紅
    [LCD.color( 30, 10, 40), LCD.color( 80, 40,100), LCD.color(140,100,160), LCD.color(255, 60,150)],

    # 4. 深棕背景｜卡其 × 紅
    [LCD.color( 40, 25, 10), LCD.color(100, 70, 40), LCD.color(170,150,110), LCD.color(220, 30, 30)],

    # 5. 深灰背景｜灰階 × 螢光藍
    [LCD.color( 20, 20, 20), LCD.color( 60, 60, 60), LCD.color(150,150,150), LCD.color(  0,200,255)],

    # 6. 深藍綠背景｜藍綠 × 黃
    [LCD.color(  5, 30, 35), LCD.color( 20, 80, 90), LCD.color( 60,130,160), LCD.color(255,220,  0)],

    # 7. 深酒紅背景｜暖色系 × 橘紅
    [LCD.color( 40, 10, 15), LCD.color(120, 40, 50), LCD.color(190,120,120), LCD.color(255, 80,  0)],

    # 8. 深藍背景｜鋼藍 × 螢光綠
    [LCD.color(  5, 15, 40), LCD.color( 30, 50,100), LCD.color( 80,110,160), LCD.color(  0,255,120)],

    # 9. 深紫灰背景｜紫灰 × 青綠
    [LCD.color( 25, 20, 35), LCD.color( 70, 60, 90), LCD.color(140,130,160), LCD.color(  0,220,200)],

    #10. 深咖啡背景｜奶茶 × 螢光紅
    [LCD.color( 35, 20, 10), LCD.color( 90, 60, 30), LCD.color(190,160,120), LCD.color(255, 40, 40)],

    #11. 夜黑藍背景｜冷灰 × 電子藍
    [LCD.color(  0,  5, 15), LCD.color( 10, 20, 40), LCD.color(120,130,150), LCD.color( 50,180,255)]
]

def spin(value , length , color):
    x = math.sin(math.radians(value*6))
    y = math.cos(math.radians(value*6))
    LCD.line(cx,cy,int(length*x+cx),int(-length*y+cy),color)
    
def watch(factor , colorSet):
    
    now = list(time.localtime())
    r = factor * 120
    h = now[3]
    if h > 12: h = h-12
    spin((now[4]/60 + h)*5,r*5/12,color[colorSet][1])
    spin(now[4],r*10/12,color[colorSet][2])
    spin(now[5],r*11/12,color[colorSet][3])
    LCD.show()
    LCD.fill(color[colorSet][0])

while True:
    watch(0.3,7)# 中央 x , y , scale , colorSet
    time.sleep(1)

