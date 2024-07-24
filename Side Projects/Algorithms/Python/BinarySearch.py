from typing import Any
from MergeSort import MergeSort

def BinarySearch(begin: int, end: int, lst: list[Any], x: Any) -> int:
    if begin > end:
        return -1

    mid = (begin + end) // 2
    if lst[mid] == x:
        return mid

    if lst[mid] < x:
        return BinarySearch(mid + 1, end, lst, x)

    return BinarySearch(begin, mid - 1, lst, x)

if __name__ == "__main__":
    lst = [2, 4, 5, 8, 99, 34, 5, 42, 56, 0, 88, 12, 45]
    print(f"List: {lst}")

    lst = MergeSort(lst)
    print(f"Merge sorted: {lst}")

    num = eval(input("Enter a number to search for: "))
    print(f"Index of {num} in list: {BinarySearch(0, len(lst) - 1, lst, num)}")
