#include <print>

//Fill in the code everywhere below the //***********************
//comments
//make sure to read all the comments
//do not alter any code in place, just add code as needed

//***********************
//fill in your student number
constexpr auto studentnumber = "FFLADA001";

// operators, do not worry about precedence
// assume that all operators have the same precedence
// i.e. if the expression is a + b * c, assume ((a + b) * c)
// alternatively: just evaluate left to right

struct Operator {};
struct Add: public Operator {};
struct Subtract: public Operator {};
struct Multiply: public Operator {};
struct Divide: public Operator {}; //division by zero is legal and should give 0

template <typename T>
concept is_operator = std::derived_from<T, Operator>; 

template <int N>
struct Num {
    static void print([[maybe_unused]]const bool answer);
};

//forward declaration of struct Expr
//used to build up concept to check that Left and Right are either expressions or numbers
template <is_operator Op, typename Left, typename Right>
struct Expr; //note, no {}

//base case 1, any T is not a number
template <typename T>
constexpr auto is_num = false;

//Only Num<number> is a number
template <int N>
constexpr auto is_num<Num<N>> = true;

//base case for expr: any old expression is not valid
template <typename T>
constexpr auto is_expr = false;

//Only expressions in the right format are valid.
template <is_operator Op, typename Left, typename Right>
constexpr auto is_expr<Expr<Op, Left, Right>> = true;

// Now combine the two, a *valid( expression is either a number or and expr, as defined above)
// Concept: T is either Num<N> or Expr<Op, L, R>
template <typename T>
concept is_valid_expr = is_num<T> || is_expr<T>;

//Now we can define an expression
//Op is constraint to Add/Sub/Mul/div
//Left & Right cannot be constrained in the template
//we cannot differ from the first (forwarded) definition
template <is_operator Op, typename Left, typename Right>
struct Expr {
    //Instead we use a static_assert for Left
    static_assert(is_valid_expr<Left>);
    //and Right to trigger a compile error if they are not valid expressions 
    static_assert(is_valid_expr<Right>);
    static void print(const bool answer = true);
};


// EVALUATE - Base case
template <typename E>
static constexpr auto Evaluate = 0; 

// PART 1: Implement specializations of the **Evaluate** variable for each case

// Create a specialization of Evaluate for Num<N> that returns the number itself
// This takes a single int template parameter
// and evaluates Num<N>
//***********************
template<int N>
constexpr auto Evaluate<Num<N>> = N;

// Create specializations of Evaluate for Expr with each operator (
// Each Expr specialization should accept two template parameters:
// Left and Right
// and recursively evaluate the left and right operands,
// then combine them using the appropriate operation
// You can use the code above the concept is_valid_expr for inspiration
// You can also sneak a peak at the print method below how these Evaluate 
// compile-time variables are invoked
// 

//***********************
//Add
template<typename Left, typename Right>
constexpr auto Evaluate<Expr<Add, Left, Right>> = Evaluate<Left> + Evaluate<Right>;

//***********************
//Subtract
template<typename Left, typename Right>
constexpr auto Evaluate<Expr<Subtract, Left, Right>> = Evaluate<Left> - Evaluate<Right>;

//***********************
//Multiply
template<typename Left, typename Right>
constexpr auto Evaluate<Expr<Multiply, Left, Right>> = Evaluate<Left> * Evaluate<Right>;

//***********************
//Divide
// For division by zero, set it to 0 instead of crashing
template<typename Left, typename Right>
constexpr auto Evaluate<Expr<Divide, Left, Right>> = (Evaluate<Right> == 0) ? 0 : Evaluate<Left> / Evaluate<Right>;


// PART 2: Implement the print() methods for Num and Expr
template <int N>
void Num<N>::print([[maybe_unused]]const bool answer) 
{
    std::print("{}", N);
}

template <is_operator Op, typename Left, typename Right>
void Expr<Op, Left, Right>::print(const bool answer) 
{
    // output the expression in the format: (left op right)
    // with the operator symbol in the middle and the brackets next to left and right
    //***********************

    std::print("(");
    Left::print(false);

    if constexpr (std::same_as<Op, Add>)
        std::print(" + ");
    else if constexpr (std::same_as<Op, Subtract>)
        std::print(" - ");
    else if constexpr(std::same_as<Op, Multiply>)
        std::print(" * ");
    else
        std::print(" / ");

    Right::print(false);
    std::print(")");

    //!!! keep these lines as is.
    if (answer) {
        std::println(" = {}", Evaluate<Expr<Op, Left, Right>>);
    }
}

//!!!!!!!!!!!!!!!!!!!!!!!

int main() {
    using expr0 = Expr<Divide, Num<1>, Num<0>>; //(1 / 0) = 0
    using expr1 = Expr<Add, Num<5>, Num<3>>; //(5 + 3) = 8
    using expr2 = Expr<Multiply, Expr<Subtract, Num<11>, Num<3>>, Num<2>>; //((11 - 3) * 2) = 16
    
    std::println("Result: {}", Evaluate<expr0>);
    //prints: "Result: 0"
    //static_assert(Evaluate<expr0> == 0);

    std::println("(5 + 3) evaluates to: {}", Evaluate<expr1>);
    //prints: "((5 + 3) * 2) evaluates to: 8"
    
    expr1::print();
    //prints: "(5 + 3) = 8"
    //static_assert(Evaluate<expr1> == 8);

    std::println("Result: {}", Evaluate<expr2>); 
    //prints "Result: 16"
    //static_assert(Evaluate<expr2> == 16);
    
    expr2::print();
    //prints "((11 - 3) * 2) = 16"
        
    std::println("{}", studentnumber);
    
    return 0;
}
