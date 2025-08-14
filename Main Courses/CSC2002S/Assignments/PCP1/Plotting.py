import sys
import csv
import matplotlib.pyplot as plt
from collections import defaultdict

if len(sys.argv) != 2:
    print("No arguments provided!")
    print("Correct usage:")
    print("python Plotting.py <path_csv_file>")
    exit()

csvFilePath = sys.argv[1]

# Collect all speedups per GateSize
speedupMap = defaultdict(list)

with open(csvFilePath, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        gateSize = int(row["GateSize"]) if "GateSize" in row else int(row.get("GateSize", 0))
        serialTime = float(row["SerialTimeMS"])
        parallelTime = float(row["ParallelTimeMS"])

        # gateSizes.append(gateSize)
        # speedups.append(serial_time / parallel_time)  # speedup = serial / parallel
        if parallelTime > 0:
            speedup = serialTime / parallelTime
            speedupMap[gateSize].append(speedup)
        # data.append([gateSize, speedup])

# Sort by GateSize
# data.sort(key=lambda x: x[0])
# gateSizes = [d[0] for d in data]
# speedups = [d[1] for d in data]

gateSizes = sorted(speedupMap.keys())
averageSpeedups = [sum(speedupMap[g]) / len(speedupMap[g]) for g in gateSizes]

plt.figure(figsize=(8,5))
plt.plot(gateSizes, averageSpeedups, marker='o', linestyle='-', color='b', label="Measured speedup")
plt.xlabel("Input size (GateSize)")
plt.ylabel("Speedup")
plt.title("Parallel Speedup vs Input Size")
plt.grid(True)
plt.legend()

# We can't show a window in WSL
# plt.show()

plt.savefig("SpeedupPlot.png")
print("Plot saved to SpeedupPlot.png")
