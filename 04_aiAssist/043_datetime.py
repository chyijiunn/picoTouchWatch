import matplotlib.pyplot as plt
from datetime import datetime

data = open('record')

x = []
y = []

# 解析資料
for line in data:
    x_str, y_str = line.rstrip().split("-")
    x.append(datetime.strptime(x_str, "%H:%M:%S"))
    y.append(float(y_str))

# 繪圖
plt.figure(figsize=(8, 4))
plt.plot(x, y, marker="o")
plt.xlabel("Time")
plt.ylabel("Acceleration (Y)")
plt.title("Acceleration vs Time")
plt.grid(True)
plt.tight_layout()
plt.show()
