from typing import Any
from copy import deepcopy

def InsertionSort(lst: list[Any]) -> list[Any]:
    res = deepcopy(lst)

    for i in range(1, len(res)):
        key = res[i]

        j = i - 1
        while (j >= 0) and (key < res[j]):
            res[j + 1] = res[j]
            j -= 1

        res[j + 1] = key

    return res

if __name__ == "__main__":
    print(InsertionSort([38, 27, 43, 10, 1, 38]))
