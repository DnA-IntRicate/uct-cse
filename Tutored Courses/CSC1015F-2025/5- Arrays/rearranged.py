# Given a sorted array, rearrange it such that the largest element is at index 0,
# the smallest at 1, the second-largest at 2, and so on.
# Lebeko Poulo
# 19/03/2025

arr = list(map(int, input("Enter sorted numbers separated by spaces:\n").split()))  # Take input
n = len(arr)  # Length of the array

low = 0  # Pointer to the smallest element
high = n - 1  # Pointer to the largest element

# Rearrange array without using built-in functions
i = 0
while low < high:
    # Store largest element temporarily
    temp = arr[high]
    # Shift elements to the right
    j = high
    while j > i:
        arr[j] = arr[j - 1]
        j -= 1
    arr[i] = temp
    high -= 1
    i += 2  # Move to the next even index

print("Rearranged array:", arr)
