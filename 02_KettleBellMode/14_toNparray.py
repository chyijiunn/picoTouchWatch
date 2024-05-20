import pandas as pd
import matplotlib.pyplot as plt

col_name = ['second','xyz[4]','xyz[1]']
data = pd.read_csv('record.csv')
df = pd.DataFrame(data,columns = col_name)

a1 = df['second'].to_numpy()
a2 = df['xyz[4]'].to_numpy()

plt.scatter(a1,a2)
plt.show()