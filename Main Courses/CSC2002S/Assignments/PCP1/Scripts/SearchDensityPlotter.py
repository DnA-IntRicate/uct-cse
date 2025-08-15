import sys
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools

GATE_SIZE: int = 200

if len(sys.argv) != 2:
    print("No arguments provided!")
    print("Correct usage:")
    print("python SearchDensityPlotter.py <path_csv_file>")
    exit()

csvFilePath = sys.argv[1]
speedupMap = defaultdict(list)

with open(csvFilePath, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        gateSize = int(row.get("GateSize", 0))
        if gateSize != GATE_SIZE:
            continue

        searchDensity = float(row.get("SearchDensity", 0.0))
        serialTime = float(row["SerialTimeMS"])
        parallelTime = float(row["ParallelTimeMS"])

        speedup = serialTime / parallelTime
        speedupMap[searchDensity].append(speedup)

# Sort densities for consistent legend
searchDensities = sorted(speedupMap.keys())
avgSpeedupMap = {density: sum(speedups)/len(speedups) for density, speedups in speedupMap.items()}

plt.figure(figsize=(10, 6))
colors = itertools.cycle(plt.cm.tab20.colors)

for density in searchDensities:
    color = next(colors)
    plt.scatter(GATE_SIZE, avgSpeedupMap[density], color=color, s=50)
    plt.scatter([], [], color=color, label=f"Density {density}")

plt.xlabel("Gate Size")
plt.ylabel("Speedup")
plt.title(f"Speedup vs Gate Size ({GATE_SIZE}) for Different Search Densities")
plt.grid(True)
plt.legend(fontsize='small', bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig("SearchDensityPlot.png")
print("Plot saved to SearchDensityPlot.png")
input("Press Enter to continue...")
