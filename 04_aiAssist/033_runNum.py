import time, math
from hw import LCD, IMU

LCD.fill(0)
LCD.show()
c = LCD.color(255,255,0)
c0 = LCD.color(0,0,0)
N = 0
while True:
    z_a_0 = IMU.Read_XYZ()[5]/500
    y = int(120 * z_a_0)
    LCD.line(120,120,120, 120+y, c)
    LCD.scroll(-1,0)
    z_a_1 = IMU.Read_XYZ()[5]/500
    if (y*y > 9) and (z1*z2<0): N = N + 1 # 修改 y*y > 9 的數值以適應跑步
    
    LCD.fill_rect(160,100,40,40,c0 )
    LCD.write_text(str(N),160 ,100,3,c)
    LCD.show()
    time.sleep(0.1)



