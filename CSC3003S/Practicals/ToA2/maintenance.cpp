#include <algorithm>
#include <cstdint>
#include <iostream>
#include <vector>
#include <ranges>
#include <print>


struct AvailabilityWindow
{
    uint64_t Earliest;
    uint64_t Latest;
};

constexpr bool CanBeServiced(uint64_t K, uint64_t P, const std::vector<AvailabilityWindow>& windows) noexcept
{
    uint64_t serviced = 0;
    uint64_t prevStart = 0;
    bool first = true;

    for (const auto& [earliest, latest] : windows)
    {   
        if (first)
        {
            ++serviced;
            prevStart = earliest;
            first = false;

            continue;
        }

        uint64_t requiredStart = std::max(earliest, prevStart + P);
        if (requiredStart <= latest)
        {
            ++serviced;
            prevStart = requiredStart;
        }
    }

    return serviced == K;
}

constexpr uint64_t ProcessImpl(
    uint64_t K, 
    const std::vector<AvailabilityWindow>& windows, 
    uint64_t left, 
    uint64_t right
) noexcept
{
    if (left > right)
        return left - 1;

    const uint64_t mid = left + (right - left) / 2;
    if (CanBeServiced(K, mid, windows))
        return ProcessImpl(K, windows, mid + 1, right);

    return ProcessImpl(K, windows, left, mid - 1);
}

constexpr uint64_t Process(uint64_t K, const std::vector<AvailabilityWindow>& windows) noexcept
{
    if ((K == 1) || (K > windows.size()))
        return 1;

    uint64_t left = 0; // (*std::ranges::min_element(windows, {}, &AvailabilityWindow::Latest)).Latest;
    uint64_t right = (*std::ranges::max_element(windows, {}, &AvailabilityWindow::Latest)).Latest;

    return ProcessImpl(K, windows, left, right);
}

int main(int argc, char** argv)
{
    // Speed up cin
    (void)std::cin.tie(nullptr);
    std::cin.sync_with_stdio(false);

    uint64_t N, K;
    std::cin >> N >> K;

    std::vector<AvailabilityWindow> windows(N);
    for (auto& window : windows)
    {
        uint64_t E, L;
        std::cin >> E >> L;
        window = { E, L };
    }

    const uint64_t P = Process(K, windows);
    std::println("{}", P);

    return 0;
}

/* Test case
Input:
4 3
0 5
2 6
6 9
7 9 

Ans: 4
*/

/*
8 3
23 33
24 29
199 262
433 487
619 658
628 704
652 654
687 724

Ans: 291

10 10
21 38
46 60
106 125
120 129
190 202
225 235
294 309
347 359
381 393
456 462

Ans: 23

*/