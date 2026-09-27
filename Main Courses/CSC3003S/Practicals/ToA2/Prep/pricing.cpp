#include <iostream>
#include <cstdint>


constexpr uint64_t MAX_GEMS = 822467118437ULL;

static uint64_t CostOf(uint64_t gems) noexcept
{
    uint64_t cost = 0;
    for (uint64_t j = 1; j < gems;)
    {
        const uint64_t quotient = gems / j;

        // Largest j for which gems / j == quotient.
        const uint64_t last = gems / quotient;

        // Sum of j from [j, last]:
        //
        //   j + (j+1) + ... + last
        //
        const uint64_t count = last - j + 1;
        const uint64_t sum = (j + last) * count / 2;

        cost += quotient * sum;
        j = last + 1;
    }

    return cost;
}

static uint64_t NumGems(uint64_t budget) noexcept
{
    uint64_t begin = 0;
    uint64_t end = MAX_GEMS;

    while (begin < end)
    {
        const uint64_t mid = begin + (end - begin + 1) / 2;
        if (CostOf(mid) <= budget)
            begin = mid;
        else
            end = mid - 1;
    }

    return begin;
}

int main(int argc, char** argv)
{
    uint64_t N;
    std::cin >> N;

    std::cout << NumGems(N) << '\n';
    return 0;
}
