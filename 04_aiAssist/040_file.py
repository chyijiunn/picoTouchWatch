import time 
data = open('record','w')# 'a' = append 為附加，'w' 為覆寫 
now = list(time.localtime())
data.write(str(now[3])+':'+str(now[4])+':'+str(now[5])+'\n')
data.close()