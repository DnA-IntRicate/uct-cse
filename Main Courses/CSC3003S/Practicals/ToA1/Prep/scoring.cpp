#include <iostream>
#include <vector>


static int g_Len;
static int g_Target;
static int g_MaxScore = -1;
static std::vector<int> g_Numbers;

static void FindBestScore(int index, int currentScore) noexcept
{
    if (currentScore >= g_Target)
        return;

    if (index == g_Len)
    {
        g_MaxScore = std::max(g_MaxScore, currentScore);
        return;
    }

    FindBestScore(index + 1, currentScore + g_Numbers[index]);
    FindBestScore(index + 1, currentScore * g_Numbers[index]);
}

int main(int argc, char** argv)
{
    std::cin >> g_Len;

    g_Numbers.resize(g_Len);
    for (int i = 0; i < g_Len; ++i)
        std::cin >> g_Numbers[i];

    std::cin >> g_Target;

    FindBestScore(0, 1);
    std::cout << g_MaxScore << '\n';

    return 0;
}
