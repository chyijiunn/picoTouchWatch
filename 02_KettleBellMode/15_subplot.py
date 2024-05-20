import pandas as pd
import matplotlib.pyplot as plt

col_name = ['second','xyz[4]','xyz[1]']
data = pd.read_csv('record.csv')
df = pd.DataFrame(data,columns = col_name)

a1 = df['second'].to_numpy()
a2 = df['xyz[4]'].to_numpy()
a3 = df['xyz[1]'].to_numpy()
#分上下兩圖
plt.subplot(2,1,1)
plt.scatter(a1,a2,s=0.8)
plt.subplot(2,1,2)
plt.scatter(a1,a3,s=0.7,color = 'pink')
plt.show()
