from typing import Any

def LinearSearch(begin: int, end: int, lst: list[Any], x: Any) -> int:
    if begin > end:
        return -1

    i = begin
    while i <= end:
        if lst[i] == x:
            return i

        i += 1

    return -1

if __name__ == "__main__":
    lst = [2, 4, 5, 8, 99, 34, 5, 42, 56, 0, 88, 12, 45]
    print(f"List: {lst}")

    num = eval(input("Enter a number to search for: "))
    print(f"Index of {num} in list: {LinearSearch(0, len(lst) - 1, lst, num)}")
