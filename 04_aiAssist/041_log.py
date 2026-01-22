import time, math
from hw import LCD, IMU

data = open('record','a') 

while 1:
    yg = IMU.Read_XYZ()[1]
    now = list(time.localtime())
    data.write(str(now[3])+':'+str(now[4])+':'+str(now[5])+'-'+str(yg)'\n')
    time.sleep(0.1)