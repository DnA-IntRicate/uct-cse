#include <print>
#include <string>


template <typename T, typename... Args>
requires(std::same_as<T, Args> && ...)
constexpr T max(T first, Args... rest) 
{
    T result = first;
    return ((result = std::max(result, rest)), ...);
}

//Do not change code below this line
//***********************************
static_assert(max(5, 12, 3, 8) == 12);
static_assert(max(2.71, 1.41, 3.14) == 3.14);

int main() {
    const auto maxInt = max(5, 12, 3, 8);
    std::println("Maximum of 5, 12, 3, 8: {}", maxInt);

    const auto maxDouble = max(2.71, 1.41, 3.14);
    std::println("Maximum of 3.14, 2.71, 1.41: {}", maxDouble);

    return 0;
}