#include <algorithm>
#include <iostream>
#include <cstdint>
#include <string>
#include <vector>
#include <tuple>
#include <utility>

int main(int argc, char **argv)
{
    std::string digits;
    std::cin >> digits;

    int target;
    std::cin >> target;

    const size_t N = 1 << digits.size();
    std::vector<int> subsetsOfDigits;

    for (size_t i = 0; i < digits.size(); ++i)
    {
        subsetsOfDigits.emplace_back(digits[i] - '0');
        for (size_t j = i + 1; j < digits.size(); ++j)
            subsetsOfDigits.emplace_back(std::stoi(digits.substr(i, j)));
    }

    std::vector<int> answers;
    int currentSum = 0;

    for (size_t i = 0; i < subsetsOfDigits.size(); ++i)
    {
        for (size_t j = 0; j < subsetsOfDigits.size(); ++j)
        {
            if (currentSum == target)
                break;

            const int& num = subsetsOfDigits[j];
            if (std::find(answers.begin(), answers.end(), num) != answers.end()) // Skip numbers we've already seen
                continue;

            if (currentSum + num > target)
                continue;

            currentSum += num;
            answers.emplace_back(num);
        }
    }

    for (const auto& i : answers)
        std::cout << i << '\n';

    return 0;
}
