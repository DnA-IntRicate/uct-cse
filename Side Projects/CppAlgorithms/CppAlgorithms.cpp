#include <iostream>
#include <string>
#include <algorithm>
#include <filesystem>
#include <sstream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <time.h>


inline static std::vector<std::string> Split(const std::string& input, char delim)
{
    std::vector<std::string> res;
    std::istringstream iss(input);
    std::string token;

    while (std::getline(iss, token, delim))
        res.push_back(token);

    return res;
}

// This isn't working because of the punctuation in the words and other special characters.
// Nevermind, that's not the problem.
static void SortAlphabetical(std::vector<std::string>& words)
{
    for (size_t i = 0; i < words.size() - 1; i++)
    {
        for (size_t j = 0; j < words.size() - 1; j++)
        {
            if (words[j] > words[j + 1])
                words[j].swap(words[j + 1]);

                //std::swap(words[j], words[j + 1]);
        }
    }
}

inline static int LinearSearch(const std::vector<std::string>& words, const std::string& token)
{
    int res = 0;
    for (const auto& word : words)
    {
        if (word == token)
            res++;
    }

    return res;
}

// This function assumes that the words vector is sorted in alphabetical order.
inline static int BinarySearch(const std::vector<std::string>& words, const std::string& token)
{
    int res = 0;
    int left = 0;
    int right = words.size() - 1;

    while (left <= right)
    {
        int mid = (left + right) / 2;

        if (words[mid] == token)
            res++;
        else if (words[mid] < token)    // Right chunk
        {
            right = mid - 1;
        }
        else if (words[mid] > token)    // Left chunk
        {
            left = mid + 1;
        }


    //    // Check if the token is equal to the middle element
    //    int comparison = token.compare(words[mid]);
    //    if (comparison == 0)
    //        res++;  // Target found, return the index
    //    // If the target is less than the middle element, search the left half
    //    else if (comparison < 0)
    //        right = mid - 1;
    //    // If the target is greater than the middle element, search the right half
    //    else
    //        left = mid + 1;

    //    if (words[mid] == token)
    //    {
    //        res++;
    //
    //    }
    //
    //    left += mid;
    }

//    for (size_t i = 0; i < words.size(); i++)
//    {
//        const auto& word = words[(words.size() - i) / 2];
//
//        if (word == token)
//            matches++;
//    }
//
    return res;
}

int main(int argc, char** argv)
{
    std::chrono::high_resolution_clock::time_point start = std::chrono::high_resolution_clock::now();

    std::string text;
    std::ifstream in("Text.txt", std::ios::in | std::ios::binary);

    if (in)
    {
        in.seekg(0, std::ios::end);
        size_t size = in.tellg();
        in.seekg(0, std::ios::beg);

        text.resize(size);
        in.read(&text[0], size);
        in.close();
    }

    constexpr const char* token = "fermentum";
    std::vector<std::string> words = Split(text, ' ');

    // Binary search for the word 'fermentum'

    SortAlphabetical(words);
    for (const auto& word : words)
        std::cout << word << std::endl;

    int matches = BinarySearch(words, token);

    std::cout << "Found " << matches << " occurrences of the word " << token << std::endl;

    std::chrono::high_resolution_clock::time_point end = std::chrono::high_resolution_clock::now();
    std::chrono::microseconds elapsed = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "Operation took " << elapsed.count() << " microseconds to complete." << std::endl;

    std::cin.get();
}
