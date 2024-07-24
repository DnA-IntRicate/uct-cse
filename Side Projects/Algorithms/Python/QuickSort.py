from typing import Any

def Partition(lst: list[Any], begin: int, end: int) -> int:
    pivot = lst[end]

    i = begin - 1
    for j in range(begin, end):
        if lst[j] <= pivot:
            i += 1
            lst[i], lst[j] = lst[j], lst[i]

    lst[i + 1], lst[end] = lst[end], lst[i + 1]

    return i + 1

def QuickSort(lst: list[Any], begin: int, end: int):
    if begin > end:
        return

    pivot = Partition(lst, begin, end)

    QuickSort(lst, begin, pivot - 1)
    QuickSort(lst, pivot + 1, end)

if __name__ == "__main__":
    lst = [38, 27, 43, 10, 1, 38]
    QuickSort(lst, 0, len(lst) - 1)
    print(lst)
