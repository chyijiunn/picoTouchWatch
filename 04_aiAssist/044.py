import matplotlib.pyplot as plt
from datetime import datetime

x = []
y = []
bad_lines = 0

with open("record", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        try:
            # 從最右邊切一次：可正確處理 "15:13:33--0.18" 這種負值
            t_str, a_str = line.rsplit("-", 1)

            x.append(datetime.strptime(t_str, "%H:%M:%S"))
            y.append(float(a_str))
        except Exception:
            bad_lines += 1

plt.figure(figsize=(25, 4))
plt.plot(x, y, marker="o", markersize=2, linewidth=1)
plt.xlabel("Time")
plt.ylabel("Acceleration (Y)")
plt.title("Acceleration vs Time")
plt.grid(True)
plt.tight_layout()
plt.show()

print("Total points:", len(x))
print("Skipped lines:", bad_lines)
