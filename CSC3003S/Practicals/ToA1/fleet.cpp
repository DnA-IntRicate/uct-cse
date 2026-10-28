#include <iostream>
#include <cstdint>
#include <vector>
#include <tuple>

int main(int argc, char **argv)
{
    double cb, cv, ct, T, tb, tv, tt, M, mb, mv, mt;
    std::cin >> cb >> cv >> ct >> T >> tb >> tv >> tt >> M >> mb >> mv >> mt;

    const int N = 50; // Idk what the heck to set N to
    std::vector<std::tuple<int, int, int>> combinations(N);
    for (size_t b = 0; b < N; ++b)
        for (size_t v = 0; v < N; ++v)
            for (size_t t = 0; t < N; ++t)
                combinations.emplace_back(b, v, t);

    double maxCapacity = -1.0;
    int maxB, maxV, maxT = -1;
    for (const auto& [b, v, t] : combinations)
    {
        const double tax = (b * tb) + (v * tv) + (t * tt);
        const double maintenance = (b * mb) + (v * mv) + (t * mt);

        if ((tax > T) || (maintenance > M))
            continue;

        const double capacity = (b * cb) + (v * cv) + (t * ct);
        if (capacity > maxCapacity)
        {
            maxCapacity = capacity;
            maxB = b;
            maxV = v;
            maxT = t;
        }
    }

    std::cout << maxB << " " << maxV << " " << maxT << '\n';
    return 0;
}
