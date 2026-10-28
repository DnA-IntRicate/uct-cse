#include <iostream>
#include <cstdint>
#include <vector>


// Determine 'M', the maximum possible length that will allow 'K' planks to be delivered.
constexpr uint32_t MaxLengthOfKPlanks(const std::vector<uint64_t>& lengths, const uint32_t k, uint32_t left = 1, uint32_t right = 10000000) noexcept
{
    // You are given N = 4 planks with lengths 10, 14, 15, 11. The order requests a minimum of 6 planks.
    //
    // The order can be fulfilled with 6 planks of length 7 each:
    //
    //  - The plank of length 10 is divide into one plank of length 7, and one of length 3 (which is discarded).
    //  - The plank of length 14 is divide into two planks of length 7.
    //  - The plank of length 15 is divide into two planks of length 7, and one of length 1 (which is discarded).
    //  - The plank of length 11 is divide into one plank of length 7, and one of length 4 (which is discarded).
    //  - The order can't be fulfilled with planks of length 8 or more, so 7 is the maximum length.

    if (left > right)
        return left - 1;

    const uint32_t mid = left + (right - left) / 2;

    uint64_t candidate = 0;
    for (const auto& l : lengths)
        candidate += l / mid;

    if (candidate < k)
        return MaxLengthOfKPlanks(lengths, k, left, mid - 1);

    return MaxLengthOfKPlanks(lengths, k, mid + 1, right);
}

int main(int argc, char** argv)
{
    uint32_t N;
    std::cin >> N;

    std::vector<uint64_t> lengths(N);
    for (auto& l : lengths)
        std::cin >> l;

    uint32_t K;
    std::cin >> K;

    std::cout << MaxLengthOfKPlanks(lengths, K) << '\n';
    return 0;
}
