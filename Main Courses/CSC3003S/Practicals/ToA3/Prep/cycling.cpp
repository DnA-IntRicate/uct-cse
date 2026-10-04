#include <algorithm>
#include <cstdint>
#include <iostream>
#include <ranges>
#include <unordered_map>
#include <vector>


constexpr int Sum(std::ranges::input_range auto&& range) noexcept
{
    int sum = 0;
    for (const auto& num : range)
        sum += num;

    return sum;
}

constexpr uint64_t HashIndices(int left, int right) noexcept
{
    return (static_cast<uint64_t>(left) << 32) | static_cast<uint64_t>(right);
}

int MaxPossibleScore(const std::vector<int>& scores, int left, int right, std::unordered_map<uint64_t, int>& memo) noexcept
{
    if (scores.empty())
        return 0;

    if (scores.size() == 1)
        return std::max(scores[0], 0);

    if (left >= right)
        return 0;

    uint64_t key = HashIndices(left, right);
    if (memo.contains(key))
        return memo.at(key);

    auto sliced = scores | std::views::drop(left) | std::views::take(right - left);
    int sum = Sum(sliced);

    int resLeft = MaxPossibleScore(scores, left + 1, right, memo);
    int resRight = MaxPossibleScore(scores, left, right - 1, memo);

    int res = std::max({ sum, resLeft, resRight });
    memo[key] = res;

    return res;
}

int main(int argc, char **argv)
{
    int N;
    std::cin >> N;

    std::vector<int> scores(N);
    for (auto& score : scores)
        std::cin >> score;

    std::unordered_map<uint64_t, int> memo;
    std::cout << MaxPossibleScore(scores, 0, scores.size(), memo) << '\n';

    return 0;
}
