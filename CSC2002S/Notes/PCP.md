# PCP Notes

## Amdahl's Law

``` math
S = \frac{1}{(1 - P) + \frac{P}{N}}
```

#### Where:
- **P** = fraction of the program that can be parallelized
- **N** = number of processors
- **1 − P** = fraction that's strictly sequential

``` math
S = \frac{T_1}{T_{\infty}}
```

#### Where:
- $T_1$ = Work
- $T_{\infty}$ = Span

#### Brief:
Amdahl's law asserts diminishing gains for increasing parallel processor counts - it defines the theoretical maximum limit achievable by parallel speedup even under theoretically infinite parallel processors.

---

## Speedup scaling

- **Strong scaling**: Increasing processor count under constant input size.
- **Weak scaling**: Increasing input size under constant processor count.
- **Super-linear scaling**: When the measured speedup exceeds the max theoretical speedup.
- **Moore's law**: States that the number of transistors on integrated circuits doubles approximately every two years.

---

## Threading

`Thread` can be in one of several states (`NEW`, `RUNNABLE`, `BLOCKED`, `WAITING`, `TIMED_WAITING`, `TERMINATED`)

- `RUNNABLE`:
    - The thread is ready to run but may **not currently be in execution**.
    - **IMPORTANT**: Java doesn't expose a `RUNNING` state explicitly. The JVM sees `RUNNING` as a subset of `RUNNABLE`.

- `RUNNING`:
    - The thread is in **active execution**.

### Methods

- `Thread.yield()`: Suggests that this thread may pause to let another of the same priority run.
- `wait()`: Causes the current thread to pause and releases the object's monitor.
- `notify()`: Wakes **one random thread** waiting on the object's monitor. The notified thread will re-acquire the lock before it can proceed.
- `notifyAlll()`: Like `notify()` but wakes **all threads** waiting.

### Race condition

Race condition is a type of bug in concurrent or multi-threaded programs that happens when the **behavior** of a program **depends on the relative timing or interleaving of threads**. It occurs when two or more threads access **shared data at the same time**, and at least **one thread modifies it**. This can cause the final modified data to **change unpredictably**.

#### The Fix:
- Mutual Exclusion (`synchronized` keyword)
- Atomic types
- Locks (`ReentrantLock`)

---
