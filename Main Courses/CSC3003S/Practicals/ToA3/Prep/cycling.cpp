#include <algorithm>
#include <cstdint>
#include <iostream>
#include <ranges>
#include <unordered_map>
#include <vector>


constexpr int Sum(std::ranges::input_range auto&& range) noexcept
{
    int sum = 0;
    for (const auto &num : range)
        sum += num;

    return sum;
}

constexpr uint64_t HashIndices(int left, int right) noexcept
{
    return (static_cast<uint64_t>(left) << 32) | static_cast<uint64_t>(right);
}

// A pair of <left, right> indices mapped to its score answer
typedef std::unordered_map<uint64_t, int> Memo;

int MaxPossibleScore(const std::vector<int>& scores, int left, int right, Memo& memo, int currMax = 0) noexcept
{
    if (scores.empty())
        return 0;

    if (scores.size() == 1)
        return std::max(scores[0], 0);

    uint64_t indexHash = HashIndices(left, right);
    if (memo.contains(indexHash))
        return memo.at(indexHash);

    auto sliced = scores | std::views::drop(left) | std::views::take(right);
    int sum = Sum(sliced);
    currMax = std::max(currMax, sum);

    if (sliced.empty() || (sliced.size() == 1))
        return currMax;

    int resLeft = MaxPossibleScore(scores, left + 1, right, memo, currMax);
    int resRight = MaxPossibleScore(scores, left, right - 1, memo, currMax);

    memo[HashIndices(left + 1, right)] = resLeft;
    memo[HashIndices(left, right - 1)] = resRight;

    return std::max(resLeft, resRight);
}

int main(int argc, char **argv)
{
    int N;
    std::cin >> N;

    std::vector<int> scores(N);
    for (auto& score : scores)
        std::cin >> score;

    Memo memo;
    int K = MaxPossibleScore(scores, 0, scores.size() - 1, memo);
    std::cout << K << '\n';

    return 0;
}
