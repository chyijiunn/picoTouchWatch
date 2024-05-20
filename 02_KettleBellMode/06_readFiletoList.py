data = open('record.csv')
for line in data:
    a , b , c = line.rstrip().split(',')
    print(a,b,c)
data.close()