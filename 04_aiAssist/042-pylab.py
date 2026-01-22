# install matplotlib , numpy

import numpy as np
import matplotlib.pyplot as plt

data = open('record')
a = []
time = []
yg = []

for line in data:
    a.append(line.rstrip().split('-'))
data.close()

for i in range(len(a)):
    time.append(a[i][0])
    yg.append(a[i][1])
print(yg)

plt.scatter(time,yg)
plt.show()
