#include <iostream>
#include <cstdint>

constexpr uint64_t MAX_POSSIBLE_GEMS = 1000000;

constexpr uint64_t CostOfGems(uint64_t gemCount) noexcept
{
    uint64_t res = 0;
    for (uint64_t i = 1; i < gemCount; ++i)
        res += i * (gemCount / i);

    return res;
}

// Returns the max number of gems that can be purchased given our budget 'n'.
constexpr uint64_t MaxGems(uint64_t n, uint64_t left = 1, uint64_t right = MAX_POSSIBLE_GEMS) noexcept
{
    if (left > right)
        return left - 1;

    const uint64_t mid = left + (right - left) / 2;
    if (CostOfGems(mid) > n)
        return MaxGems(n, left, mid - 1);

    return MaxGems(n, mid + 1, right);

    // Linear iterative approach
    //
    // uint64_t res = 0;
    // for (uint64_t i = 1; i < MAX_POSSIBLE_GEMS; ++i)
    // {
    //     if (CostOfGems(i) >= n)
    //         break;
    //
    //     ++res;
    // }
    //
    // return res;
}

int main(int argc, char **argv)
{
    uint64_t N;
    std::cin >> N;

    std::cout << MaxGems(N) << '\n';

    return 0;
}
