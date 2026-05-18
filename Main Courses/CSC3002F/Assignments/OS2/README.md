# CSC3002F Assignment OS2 ~ Adam Foflonker

## Preamble

This report details the methods and results used to profile and compare several **CPU Scheduling** algorithms, namely:

- **First-Come First-Serve** (FCFS)
- **Shortest Job First** (SJF)
- **Priority**
- **Multilevel Feedback Queue** (MLFQ)

All algorithm simulation, testing and data collection was performed via the **"Allegra The Barman"** simulation.

---

## Methods

### Recording

To record the required data, the `void recordCompletedOrder(DrinkOrder order)` function in `Barman.java` was implemented to emit `DrinkOrder` information into a CSV file. The CSV files are named according to the format: `"{scheduler_name}_ST{switch_time}.csv"`. All CSV files are saved to the [results](./results/) folder, relative to the project's root.

> **Note:** If the CSV file for the current test (scheduler + switch time) already exists, the new `DrinkOrder` data is appended into it.

The metrics recorded in each CSV file are:

- **PatronID**: `int`
- **Drink**: `string`
- **ArrivalTime**: `long`
- **StartTime**: `long`
- **CompletionTime**: `long`
- **ExecutionTime**: `long`
- **WaitingTime**: `long`
- **ResponseTime**: `long`
- **TurnaroundTime**: `long`
- **QueueLevel**: `int`
- **Priority**: `int`

> **Important:** The `recordCompletedOrder` function must be marked as `synchronized` since it performs **I/O** operations and can be called from multiple threads.

To actually record the data, the simulation was run multiple times on a range of different inputs using the shell script [tests.sh](tests.sh):

``` bash
readonly SEED=42

for sched in 0 1 2 3
do
    for patrons in 10 50 100
    do
        for switchTime in 0 5 20
        do
            echo "Running Scheduler $sched:"
            echo "  Patrons: $patrons"
            echo "  Switch Time: $switchTime ms"
            echo

            make run ARGS="$patrons $sched $switchTime $SEED"

            echo
            echo "Done."
            echo
        done
    done
done

```

> **Note:** A fixed seed value of `42` was used to ensure determinism,  reproducibility of results and fair testing between different schedulers.

### Validation

The data generated was validated by running the simulation on two separate machines and doing a basic diff-check between their generated CSV files - looking for any abnormalities or large discrepancies.

### Reporting

To properly represent and report the recorded data, the Python script [analysis.py](analysis.py) was written, which uses `matplotlib`, `numpy`, `pandas` and `seaborn` to represent the data in a series of plots.

The different plots generated are:

- **Plot 1**: Summary stats table (mean, median, std, min, max)
- **Plot 2**: Grouped bar chart (mean & median per metric)
- **Plot 3**: Box plots (distribution per metric)
- **Plot 4**: Effect of Context Switch Time on each metric
- **Plot 5**: Waiting time CDF (starvation & fairness check)
- **Plot 6**: Throughput (orders completed per unit time)
- **Plot 7**: Heatmap (mean waiting time)
- **Plot 8**: Radar chart (normalized metric comparison)

---

## Results






## Conclusions
