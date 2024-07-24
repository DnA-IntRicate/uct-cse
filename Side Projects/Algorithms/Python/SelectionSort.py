from typing import Any
from copy import deepcopy


def SelectionSort(lst: list[Any]) -> list[Any]:
    res = deepcopy(lst)

    for i in range(len(res) - 1):
        idxMin = i
        for j in range(i + 1, len(res)):
            if (res[idxMin] > res[j]):
                idxMin = j

        res[i], res[idxMin] = res[idxMin], res[i]

    return res


if __name__ == "__main__":
    print(SelectionSort([38, 27, 43, 10, 1, 38]))
