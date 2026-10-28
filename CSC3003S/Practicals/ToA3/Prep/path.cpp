#include <algorithm>
#include <compare>
#include <cstdint>
#include <iostream>
#include <ranges>
#include <unordered_map>
#include <vector>


struct Vec2i
{
    constexpr Vec2i(int x, int y) noexcept : x(x), y(y) {}
    constexpr Vec2i(int value) noexcept : x(value), y(value) {}
    constexpr Vec2i() noexcept = default;

    constexpr std::strong_ordering operator<=>(const Vec2i&) const noexcept = default;

    int x;
    int y;
};

// Hash function for Vec2i
namespace std
{
    template<>
    struct hash<Vec2i>
    {
        std::size_t operator()(const Vec2i& v) const noexcept
        {
            // NOTE(Adam): Yes I know... I'm assuming 64bit and that's a problem...
            //             But I'm not using golden ratio hashing cos I can't remember the number.
            return std::hash<std::size_t>{}((static_cast<std::size_t>(v.x) << 32) | static_cast<std::size_t>(v.y));
        }
    };
}

constexpr uint64_t NumberOfPaths(
    const int N,
    const std::vector<Vec2i>& obstacles,
    std::unordered_map<Vec2i, uint64_t>& memo,
    const Vec2i& pos = {1, 1}
) noexcept
{
    // Grid is too small
    if (N <= 1)
        return 0;

    // Out of bounds
    if ((pos.x > N) || (pos.y > N))
        return 0;

    // Check if this position is an obstacle
    if (std::ranges::find(obstacles, pos) != obstacles.end())
        return 0;

    // Target found
    if (pos == Vec2i(N))
        return 1;

    if (memo.contains(pos))
        return memo.at(pos);

    const Vec2i right = Vec2i(pos.x + 1, pos.y);
    const Vec2i up = Vec2i(pos.x, pos.y + 1);

    if (std::ranges::find(obstacles, right) != obstacles.end())
    {
        // Move up
        uint64_t res = NumberOfPaths(N, obstacles, memo, up);
        memo[pos] = res;

        return res;
    }
    else if (std::ranges::find(obstacles, up) != obstacles.end())
    {
        // Move right
        uint64_t res = NumberOfPaths(N, obstacles, memo, right);
        memo[pos] = res;

        return res;
    }

    uint64_t res = NumberOfPaths(N, obstacles, memo, right) + NumberOfPaths(N, obstacles, memo, up);
    memo[pos] = res;

    return res;
}

int main(int argc, char** argv)
{
    int N, K;
    std::cin >> N >> K;

    std::vector<Vec2i> obstacles(K);
    for (auto& [x, y] : obstacles)
        std::cin >> x >> y;

    std::unordered_map<Vec2i, uint64_t> memo;
    std::cout << NumberOfPaths(N, obstacles, memo) << '\n';

    return 0;
}
