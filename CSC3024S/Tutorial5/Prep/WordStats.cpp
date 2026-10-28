#include <algorithm>
#include <cassert>
#include <cctype>
#include <map>
#include <print>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

struct WordStats
{
    std::string most_frequent_word;
    int max_frequency;
    int unique_words_filtered;
    int total_words_analyzed;
};

std::string ToLower(std::string_view text)
{
    std::string result(text);
    std::ranges::transform(result, result.begin(), [](unsigned char c) { return static_cast<char>(std::tolower(c)); });

    return result;
}

// 1. Convert text to lowercase and split into words
// 2. Use std::map to count frequencies and store words
// 3. Apply lambda filters for word length >= 3
// 4. Store words in a vector and
//    Sort using std::ranges::sort with custom comparator lambda
//    The lambda compares two words case insensitively
//    (std::tolower is your friend)
// 5. print the input string in sorted word order
//    e.g. Hello dolly => dolly Hello
// 6. Return WordStats with results
WordStats analyze_words(std::string_view text)
{
    std::map<std::string, int> freqs;
    std::vector<std::string> words;

    for (auto&& part : text | std::views::split(' '))
    {
        std::string word(part.begin(), part.end());
        words.emplace_back(word);

        if (word.size() >= 3)
            ++freqs[ToLower(word)];
    }

    std::ranges::sort(words, [](const std::string& a, const std::string& b) { return ToLower(a) < ToLower(b); });
    for (const auto& word : words)
        std::print("{} ", word);

    std::println();

    WordStats res{};
    res.most_frequent_word = std::ranges::max_element(freqs, {}, [](const auto& pair) { return pair.second; })->first;
    res.max_frequency = freqs.at(res.most_frequent_word);
    res.unique_words_filtered = static_cast<int>(freqs.size());
    res.total_words_analyzed = static_cast<int>(words.size());

    return res;
}

int main()
{
    constexpr std::string_view input = "the quick brown fox jumps over the lazy dog the fox is quick";

    const auto result = analyze_words(input);

    // Use static_assert to validate compile-time results
    assert(result.max_frequency == 3); // "fox" or "quick" appears 3 times
    assert(result.unique_words_filtered == 8);
    assert(result.total_words_analyzed == 13);

    std::println("Most frequent word: {}", result.most_frequent_word);
    std::println("Frequency: {}", result.max_frequency);
    std::println("Unique words (filtered): {}", result.unique_words_filtered);
}
