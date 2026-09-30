#include <concepts>
#include <print>

// fill in your student number
const auto studentnumber = "FFLADA001";
// Fill in the section between the
/**********************************************************/

// Checking that all parameters are the same is easy
// we can just do a single pass
// ToA: O(n)
template <typename T, typename... Args>
// note that std::same_as<T, **nothing**> returns true
// so it accidentally works for 1 argument.
concept AllSameType = (std::same_as<T, Args> && ...);

// overload for zero arguments
void samesame()
{
    std::println("All arguments are the same type!");
}

// overload for 1 or more arguments
template <typename T, typename... Args>
    requires AllSameType<T, Args...>
void samesame(T first, Args... rest)
{
    // needs at least one argument
    // the requires clause will do the checking
    // if it does not fail to compile, just print the string.
    samesame();
}

// The assignment is to check that all parameters are of a different type.
// This requires checking argument 0 against all other arguments,
// argument 1 against all higher arguments and so on.
// ToA: O(n^2)

// this is the iterative version of the code you'll need to define below.
// It uses template for, do not worry how this works
// it is out-of-scope, but use it for inspiration
template <typename... Ts>
consteval bool AllDiffs(Ts... args)
{
    // the syntax is: template for(optional initialization statement; type varname: {args...})
    // compare element 0 with 0,1,2,3...
    // then element 1 with 0,1,2,3,...
    // and so on.

    // Note: in the recursive version you need to write, you can be smarter
    // and just do 0 != 1,2,3...; 1 != 2,3,... etc
    // this does only half the work.
    auto different = true;
    template for (auto a = 0; auto i : {args...})
    {
        template for (auto b = 0; auto j : {args...})
        {
            // because we cannot skip elements easily in a for in loop, we just do all
            // and test if the indexes are different
            // this extra work can be avoided in a recursive version.
            different &= ((!std::same_as<decltype(i), decltype(j)>) || (a == b));
            b++;
        }
        a++;
    }
    return different;
}

// Do not change code above this line
// #######################################################

// Recursive specialization: Handles one or more parameters
template <typename T, typename... Rest>
constexpr bool AreAllDifferent(const T &t, const Rest &...args)
{
    // First: the stopping condition, a single argument is always distinct
    if constexpr (sizeof...(args) == 0)
        return true;
    else
        return ((!std::same_as<T, Rest>) && ...) && AreAllDifferent(args...);
}

// Do not change code below this line
// #####################################

static_assert(AllDiffs(1, 3.14, "hello"));        // true
static_assert(!AllDiffs(1, 2, "hello"));          // false
static_assert(AreAllDifferent(1, 3.14, "hello")); // true
static_assert(!AreAllDifferent(1, 2, "hello"));   // false

template <typename... Args>
concept AllDifferent = requires(Args... args) {
    AreAllDifferent(args...);
};

void process()
{
    std::println("All arguments are different types!");
}

template <typename... Args>
void process(Args... args)
{
    if (AreAllDifferent(args...))
    {
        process();
    }
    else
    {
        std::println("not different");
    }
}

int main()
{
    process();                   // ✓ Zero arguments (base case: true)
    process(1);                  // ✓ One argument (Rest is empty, base case: true)
    process(1, 3.14, "hello");   // ✓ All different types
    process(1, 'a', 2.5f, "hi"); // ✓ All different types
    process(1, 2, "hi");         // must print not different
}
