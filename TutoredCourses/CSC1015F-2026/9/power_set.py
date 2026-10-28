# Adam Foflonker
# 15/05/26
# Assignment 9 Question 4 sample solution

import sys


def power_set(arr: list[int], i: int = 0) -> list[list[int]]:
    if i == len(arr):
        return []

    rest = power_set(arr, i + 1)
    return rest + [subset + [arr[i]] for subset in rest]


def main():
    input_set = list(map(int, input("Enter elements of the set separated by spaces:\n").split(" ")))

    pow_set = power_set(input_set)
    print(f"There are {len(pow_set)} subsets.")
    print("The subsets making up the power set are:\n" + "\n".join(f"{_set}" for _set in pow_set))


if __name__ == "__main__":
    sys.setrecursionlimit(30000)
    main()
