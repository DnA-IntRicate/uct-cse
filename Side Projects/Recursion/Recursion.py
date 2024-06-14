# A collection of common applications of recursive logic

def Factorial(n: int) -> int:
    if (n == 0) or (n == 1):
        return 1

    return n * Factorial(n - 1)

def Power(base: int, exp: int) -> float:
    if exp == 0:
        return 1

    return base * Power(base, exp - 1)

def FibonacciNumber(index: int) -> int:
    if (index == 0) or (index == 1):
        return 0

    if index == 2:
        return 1

    return FibonacciNumber(index - 1) + FibonacciNumber(index - 2)

def FibonacciSeries(start: int, stop: int, result: list[int] = []) -> list[int]:
    if start > stop:
        return []

    if start == stop:
        return result

    result.append(FibonacciNumber(start))

    return FibonacciSeries(start + 1, stop, result)

def ReverseString(s: str) -> str:
    if len(s) <= 1:
        return s

    return s[-1] + ReverseString(s[:-1])

def Count(n: int, lst: list[int]) -> int:
    if len(lst) == 0:
        return 0

    if len(lst) == 1:
        return 1 if lst[0] == n else 0

    res = 0
    if lst[0] == n:
        res += 1

    return res + Count(n, lst[1:])

if __name__ == "__main__":
    n = eval(input("Enter a number: "))
    factorial = Factorial(n)
    squared = Power(n, 2)
    cubed = Power(n, 3)
    fibNumber = FibonacciNumber(n)
    fibSeries = FibonacciSeries(1, n + 1)

    print(f"Factorial: {factorial}")
    print(f"Squared: {squared}")
    print(f"Cubed: {cubed}")
    print(f"Fibonacci number: {fibNumber}")
    print(f"Fibonacci series: {fibSeries}")
    print(f"\"Hello, World!\" reversed is: {ReverseString("Hello, World!")}")

    lst = [2, 4, 5, 6, 88, 9, 5, 9, 6, 7, 3, 4, 5, 9, 8, 7, 9, 10, 9, 55, 6, 7, 9]
    print(f"Count: {Count(n, lst)}")
