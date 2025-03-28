# Given a sorted array, rearrange it such that the largest element is at index 0, 
# the smallest at 1, the second-largest at 2, and so on.
# Lebeko Poulo
# 19/03/2025

arr = list(map(int, input("Enter sorted numbers separated by spaces:\n").split()))  # Take input

n = len(arr)  # Length of the array
rearranged = [0] * n  # Placeholder for the rearranged array

low = 0  # Pointer to the smallest element
high = n - 1  # Pointer to the largest element

for i in range(n):
    if i % 2 == 0:  # Even index → pick largest element
        rearranged[i] = arr[high]
        high -= 1
    else:  # Odd index → pick smallest element
        rearranged[i] = arr[low]
        low += 1

print("Rearranged array:", rearranged)
