#include <algorithm>
#include <iostream>
#include <print>
#include <unordered_map>
#include <utility>
#include <vector>


enum class Color
{
    None = 0,
    Red,
    Green,
    Blue
};

// Create a hash function for my pair key
namespace std
{
    template<>
    struct hash<std::pair<int, Color>>
    {
        std::size_t operator()(const std::pair<int, Color>& pair) const noexcept
        {
            const auto& [i, c] = pair;

            std::size_t h1 = std::hash<int>{}(i);
            std::size_t h2 = std::hash<Color>{}(c);

            // I forgot the golden ratio number used in hashing, so here's whatever this is
            // Please don't ask me about this... I pulled it out of my a$$.
            return h1 ^ (0x97993ce) | (h2 << 8);
        }
    };
}

struct Cost
{
    constexpr Cost(int r, int g, int b) noexcept : r(r), g(g), b(b) {}
    constexpr Cost() noexcept = default;

    int r;
    int g;
    int b;
};

constexpr int MinCost(
    const std::vector<Cost>& costs,
    std::unordered_map<std::pair<int, Color>, int>& memo,
    int i = 0,
    Color col = Color::None
) noexcept
{
    if (i >= costs.size())
        return 0;

    const auto key = std::make_pair(i, col);
    if (memo.contains(key))
        return memo.at(key);

    const int next = i + 1;

    if (col == Color::Red)
    {
        int res = costs[i].r + std::min(MinCost(costs, memo, next, Color::Green), MinCost(costs, memo, next, Color::Blue));
        memo[key] = res;

        return res;
    }

    if (col == Color::Green)
    {
        int res = costs[i].g + std::min(MinCost(costs, memo, next, Color::Red), MinCost(costs, memo, next, Color::Blue));
        memo[key] = res;

        return res;
    }

    int res = costs[i].b + std::min(MinCost(costs, memo, next, Color::Red), MinCost(costs, memo, next, Color::Green));
    memo[key] = res;

    return res;
}

int main(int argc, char** argv)
{
    int N;
    std::cin >> N;

    std::vector<Cost> costs(N);
    for (auto& [r, g, b] : costs)
        std::cin >> r >> g >> b;

    std::unordered_map<std::pair<int, Color>, int> memo;
    int minCost = std::min(
        {
            MinCost(costs, memo, 0, Color::Red),
            MinCost(costs, memo, 0, Color::Green),
            MinCost(costs, memo, 0, Color::Blue)
        }
    );

    std::println("{}", minCost);
    return 0;
}

/**
7
4 2 1
4 5 2
4 2 7
5 8 6
3 6 6
4 5 2
10 3 9

Ans: 20
*/
