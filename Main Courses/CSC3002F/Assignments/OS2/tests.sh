#!/bin/bash

# Arg[1] = Number of Patrons
# Arg[2] = Scheduler (0 = FCFS, 1 = SJF, 2 = Priority, 3 = MLFQ with aging)
# Arg[3] = Context switch Time
# Arg[4] = Seed (Leave this at 42 for all tests to keep results consistent and deterministic)

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
