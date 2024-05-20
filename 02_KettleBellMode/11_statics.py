import pandas as pd
import matplotlib.pyplot as plt
col_name = ['second','xyz[4]','xyz[1]']
data = pd.read_csv('record.csv')
df = pd.DataFrame(data,columns = col_name)

#print(df['xyz[4]'])
print(df['xyz[1]'].describe())