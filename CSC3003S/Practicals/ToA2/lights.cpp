#include <cmath>
#include <iostream>
#include <print>


typedef long double floatmax;

constexpr floatmax F(floatmax hA, floatmax hB, floatmax xB, floatmax xP) noexcept
{
    const floatmax lA = std::sqrt(std::pow(xP, 2) + std::pow(hA, 2));
    const floatmax lB = std::sqrt(std::pow((xB - xP), 2) + std::pow(hB, 2));

    return lA + lB;
}

constexpr floatmax ProcessImpl(
    floatmax hA, 
    floatmax hB, 
    floatmax xB, 
    floatmax L,
    floatmax left,
    floatmax right
) noexcept
{
    if (left > right)
        return left;

    const floatmax mid = left + (right - left) / 2;
    const floatmax candidate = F(hA, hB, xB, mid);

    if (candidate == L)
        return mid;

    if (candidate > L)
        return ProcessImpl(hA, hB, xB, L, left, mid - 1.0e-8);

    return ProcessImpl(hA, hB, xB, L, mid + 1.0e-8, right);
}

// Find xP in [xL, xU] such that f(xP) = L.
constexpr floatmax Process(
    floatmax hA, 
    floatmax hB, 
    floatmax xB, 
    floatmax xL, 
    floatmax xU, 
    floatmax L
) noexcept
{
    floatmax left = xL;
    floatmax right = xU;

    return ProcessImpl(hA, hB, xB, L, left, right);
}

int main(int argc, char** argv)
{
    floatmax hA, hB, xB, xL, xU, L;
    std::cin >> hA >> hB >> xB >> xL >> xU >> L;

    const floatmax xP = Process(hA, hB, xB, xL, xU, L);
    std::println("{0:.8f}", xP);

    return 0;
}

/* Test case
Input:
91.0 84.0
73.0
39.0 72.0
196.0

Ans: 64.56417204
*/