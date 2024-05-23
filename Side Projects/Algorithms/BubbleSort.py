from typing import Any
from copy import deepcopy

def BubbleSort(lst: list[Any]) -> list[Any]:
    res = deepcopy(lst)

    for i in range(len(res)):
        for j in range(len(res) - i - 1):
            if res[j] > res[j + 1]:
                res[j], res[j + 1] = res[j + 1], res[j]

    return res


if __name__ == "__main__":
    print(BubbleSort([38, 27, 43, 10, 1, 38]))
