import sys
import csv
import matplotlib.pyplot as plt
from collections import defaultdict

if len(sys.argv) != 3:
    print("Incorrect usage!")
    print("Usage: python Plotting.py <path_csv_file_current> <path_csv_file_nightmare>")
    exit()

csvFileCurrent = sys.argv[1]
csvFileNightmare = sys.argv[2]

def LoadSpeedupFromCSV(csvPath: str):
    speedup_map = defaultdict(list)
    with open(csvPath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            gateSize = int(row["GateSize"]) if "GateSize" in row else int(row.get("GateSize", 0))
            serialTime = float(row["SerialTimeMS"])
            parallelTime = float(row["ParallelTimeMS"])

            if parallelTime > 0:
                speedup = serialTime / parallelTime
                speedup_map[gateSize].append(speedup)

    gate_sizes = sorted(speedup_map.keys())
    avg_speedups = [sum(speedup_map[g]) / len(speedup_map[g]) for g in gate_sizes]

    return gate_sizes, avg_speedups

# Load both datasets
gateSizesCurrent, avgSpeedupsCurrent = LoadSpeedupFromCSV(csvFileCurrent)
gateSizesNightmare, avgSpeedupsNightmare = LoadSpeedupFromCSV(csvFileNightmare)

# Plot
plt.figure(figsize=(8, 5))
plt.plot(gateSizesCurrent, avgSpeedupsCurrent, marker='o', linestyle='-', color='red',
         label="Measured speedup (4-Core Ryzen 3 7320U) @ Search density 0.35")
plt.plot(gateSizesNightmare, avgSpeedupsNightmare, marker='s', linestyle='--', color='purple',
         label="Measured speedup (Nightmare) @ Search density 0.1")

plt.xlabel("Dungeon Gate Size (Input)")
plt.ylabel("Speedup")
plt.title("Parallel Speedup vs Dungeon Gate Size")
plt.grid(True)
plt.legend()

plt.savefig("SpeedupPlot.png")
print("Plot saved to SpeedupPlot.png")
input("Press Enter to continue...")
