import pylab
data = open('record0.csv')
a = []
sec = []
xyz4 = []

for line in data:
    a.append(line.rstrip().split(','))
data.close()

for i in range(len(a)):
    sec.append(a[i][0])
    xyz4.append(a[i][1])

pylab.scatter(sec,xyz4)
pylab.show()
