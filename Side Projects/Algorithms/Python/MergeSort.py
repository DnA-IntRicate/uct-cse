from typing import Any

def Merge(left: list[Any], right: list[Any]) -> list[Any]:
    res = []
    idxLeft, idxRight = 0, 0

    while (idxLeft < len(left)) and (idxRight < len(right)):
        if left[idxLeft] < right[idxRight]:
            res.append(left[idxLeft])
            idxLeft += 1
            continue

        res.append(right[idxRight])
        idxRight += 1

    return res + left[idxLeft:] + right[idxRight:]

def MergeSort(lst: list[Any]) -> list[Any]:
    if len(lst) <= 1:
        return lst

    mid = len(lst) // 2
    left = lst[:mid]
    right = lst[mid:]

    return Merge(MergeSort(left), MergeSort(right))


if __name__ == "__main__":
    print(MergeSort([38, 27, 43, 10, 1, 38]))
