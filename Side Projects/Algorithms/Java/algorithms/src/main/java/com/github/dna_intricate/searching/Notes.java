// Linear search:
    // Best-case: O(1)           - Target index is first
    // Worst-case: O(n)          - Target index is last or dne
    // Average-case: O(n)

// Binary search:
    // Best-case: O(1)           - Target index is in the middle
    // Worst-case: O(log n)      - Target index is last or dne
    // Average-case: O(log n)

// Bubble sort:
    // Best-case: O(n)           - Input is already sorted
    // Worst-case: O(n^2)        - Input is in reverse order
    // Average-case: O(n^2)

// Insertion sort:
    // Best-case: O(n)           - Input is already sorted
    // Worst-case: O(n^2)        - Input is in reverse order
    // Average-case: O(n^2)
// In-place sort. Forward iterates and selects each element as a key, then reverse iterates to find which index
// that key should be inserted into the array to sort.

// Merge sort:
    // Best-case: O(n log n)     - Input is already or nearly sorted
    // Worse-case: O(n log n)    - Input is in reverse order
    // Average-case: O(n log n)
// Divide-and-conquer. Recursively divides into smaller subarrays, sorts them and merges back to obtain a sorted array.

// Quick sort:
    // Best-case: O(n log n)     - Chosen pivot divides the input into equal halves
    // Worst-case: O(n^2)        - Input is already sorted and chosen pivot is smallest or largest element
    // Average-case: O(n log n)
// Divide-and-conquer. Picks an element as pivot (usually first or last) and partitions list around the pivot.

// Selection sort:
    // Best-case: O(n^2)     - Input is already sorted
    // Worst-case: O(n^2)    - Input is in reverse order
    // Average-case: O(n^2)
// Repeatedly selects smallest/largest element from unsorted part and moves it to the sorted part by swapping it with first unsorted.
