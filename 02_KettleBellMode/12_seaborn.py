import pandas as pd
import matplotlib.pyplot as plt
import seaborn
col_name = ['second','xyz[4]','xyz[1]']
data = pd.read_csv('record.csv')
df = pd.DataFrame(data,columns = col_name)
seaborn.pairplot(df)
plt.show()