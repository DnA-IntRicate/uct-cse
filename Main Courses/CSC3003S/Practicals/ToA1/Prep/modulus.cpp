#include <iostream>
#include <cstdint>


int main(int argc, char** argv)
{
    uint32_t n, z;
    std::cin >> n >> z;

    int count = 0;
    for (uint32_t x = 1; x < n; ++x)
    {
        for (uint32_t y = 1; y < n; ++y)
        {
            if (((x * y) % n) == z)
                ++count;
        }
    }

    std::cout << count << '\n';
    return 0;
}
