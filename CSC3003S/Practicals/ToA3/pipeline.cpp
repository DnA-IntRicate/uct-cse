#include <algorithm>
#include <iostream>
#include <print>
#include <unordered_map>
#include <utility>
#include <vector>


// Create a hash function for my pair key
namespace std
{
    template<>
    struct hash<std::pair<int, int>>
    {
        std::size_t operator()(const std::pair<int, int>& pair) const noexcept
        {
            const auto& [row, col] = pair;

            std::size_t h1 = std::hash<int>{}(row);
            std::size_t h2 = std::hash<int>{}(col);

            // I forgot the golden ratio number used in hashing, so here's whatever this is
            // Please don't ask me about this... I pulled it out of my a$$.
            return h1 ^ (0x97993ce) | (h2 << 8);
        }
    };
}

constexpr int ComputePath(
    const std::vector<std::vector<int>>& grid,
    std::unordered_map<std::pair<int, int>, int>& memo,
    int row = 0,
    int col = 0
) noexcept
{
    if ((row == grid.size() - 1) && (col == grid[0].size() - 1))
        return grid[row][col];

    if (row == grid.size() - 1)
        return std::max(grid[row][col], ComputePath(grid, memo, row, col + 1));

    if (col == grid[0].size() - 1)
        return std::max(grid[row][col], ComputePath(grid, memo, row + 1, col));

    const auto key = std::make_pair(row, col);
    if (memo.contains(key))
        return memo.at(key);

    int res = std::max(grid[row][col], std::min(ComputePath(grid, memo, row + 1, col), ComputePath(grid, memo, row, col + 1)));
    memo[key] = res;

    return res;
}

int main(int argc, char** argv)
{
    int R, C;
    std::cin >> R >> C;

    std::vector<std::vector<int>> grid(R);
    for (auto& col : grid)
        col.resize(C);

    for (int row = 0; row < R; ++row)
        for (int col = 0; col < C; ++col)
            std::cin >> grid[row][col];

    std::unordered_map<std::pair<int, int>, int> memo;
    std::println("{}", ComputePath(grid, memo));

    return 0;
}

/**
1 5
3 1 7 2 5

Ans: 7

*/

/**
4 2
5 11
13 17
5 2
13 12

Ans: 13
*/

/**
5 1
2
8
3
6
1

Ans: 8
*/
