import time, math
from hw import LCD, IMU
c = LCD.color(255,255,0)

walkNum = 0
#讀取紀錄
def read_record():
    try:
        with open("record", "r") as f:
            return int(f.read().strip())
    except:
        return 0
#寫新紀錄 
def write_record(value):
    with open("record", "w") as f:
        f.write(str(value))

#將紀錄讀取出
record = read_record()

while 1:
    LCD.fill(0)
    yg0 = IMU.Read_XYZ()[1]-1
    time.sleep(0.05)
    yg1 = IMU.Read_XYZ()[1]-1
    
    if yg0 * yg1 < 0:
        walkNum = walkNum + 1
        if walkNum >= record:
            record = walkNum
            write_record(record)
        LCD.write_text(str(walkNum),120,120,3,c)#寫現在步數
        LCD.write_text('Record',50,30,3,c)		#title
        LCD.write_text(str(record),100,60,3,c)		#寫最高紀錄

        LCD.show()
