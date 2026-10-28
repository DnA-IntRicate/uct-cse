import numpy as np
import matplotlib.pyplot as plt

# Given data: number of comparisons for different n values
n_values = np.array([1, 10, 100, 1000, 5000, 10000, 20000, 30000, 40000, 50000])

# Experimental comparisons (best, average, worst case)
insert_best = np.array([0, 20, 400, 9000, 56000, 120000, 250000, 390000, 540000, 700000])
insert_avg = np.array([0, 43, 828, 13734, 86103, 190267, 408289, 637011, 878550, 1116470])
insert_worst = np.array([0, 80, 1600, 25000, 160000, 360000, 780000, 1200000, 1600000, 2000000])

search_best = np.array([5000, 10000, 20000, 30000, 40000, 45000, 49000, 49500, 49800, 50000])
search_avg = np.array([5000, 18386, 34804, 50757, 62206, 67107, 71256, 73404, 74716, 75295])
search_worst = np.array([5000, 25000, 45000, 65000, 90000, 110000, 130000, 145000, 160000, 170000])

# Compute theoretical O(log n) comparisons for search and insertion
log_n = np.log2(n_values)

# For Insertion (Theoretical O(log n))
c_insert = insert_avg[len(n_values) // 2] / (log_n[len(n_values) // 2] * n_values[len(n_values) // 2])
log_n_scaled_insert = c_insert * log_n * n_values

# For Search (Theoretical O(log n))
c_search = search_avg[len(n_values) // 2] / log_n[len(n_values) // 2]
log_n_scaled = c_search * log_n

# Create figure with two side-by-side plots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Insertion plot
axes[0].plot(n_values, insert_best, label="Best Case Insert", marker='^', linestyle='dotted', color='green')
axes[0].plot(n_values, insert_avg, label="Experimental (Avg Case) Insert", marker='o', linestyle='-', color='blue')
axes[0].plot(n_values, insert_worst, label="Worst Case Insert", marker='s', linestyle='--', color='red')
axes[0].plot(n_values, log_n_scaled_insert, label="Theoretical O(log n) Insert", marker='x', linestyle='-.', color='black')

axes[0].set_xlabel("Number of Elements (n)")
axes[0].set_ylabel("Number of Comparisons")
axes[0].set_title("AVL Tree Insertion")
axes[0].legend()
axes[0].grid(True)
axes[0].set_xscale("log")
axes[0].set_yscale("log")

# Search plot
axes[1].plot(n_values, search_best, label="Best Case Search", marker='^', linestyle='dotted', color='green')
axes[1].plot(n_values, search_avg, label="Experimental (Avg Case) Search", marker='o', linestyle='-', color='blue')
axes[1].plot(n_values, search_worst, label="Worst Case Search", marker='s', linestyle='--', color='red')
axes[1].plot(n_values, log_n_scaled, label="Theoretical O(log n) Search", marker='x', linestyle='-.', color='black')

axes[1].set_xlabel("Number of Elements (n)")
axes[1].set_ylabel("Number of Comparisons")
axes[1].set_title("AVL Tree Search")
axes[1].legend()
axes[1].grid(True)
axes[1].set_xscale("log")
axes[1].set_yscale("log")

plt.tight_layout()
plt.show()
