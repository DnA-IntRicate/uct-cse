#include <cassert>
#include <print>
#include <exception>
#include <algorithm>


std::string studentnumber = "FFLADA001";

namespace math { // Do not indent after a namespace
class Polynomial
{
    // Do not alter these data members
    size_t length;
    int degree_;
    double* data;

    // Helper: recalculate degree_ by finding highest non-zero coefficient
    constexpr void update_degree()
    {
        degree_ = -1;
        for (auto i = length; i > 0; )
        {
            if (data[--i] != 0.0)
            {
                degree_ = i;
                return;
            }
        }
    }

    //private default constructor, only for internal use
    // constexpr Polynomial() noexcept: length(0), degree_(-1), data(nullptr) {}

    constexpr void example_exception() const {
        throw std::out_of_range("Out of range error");
    }

public:
    //diagnostic stuff, no not change
    // Accessors
    constexpr auto degree() const noexcept { return degree_; }
    constexpr auto size() const noexcept { return length; }
    constexpr auto has_moved() const noexcept { return nullptr == data; }

    //constructor empty polynomial, initialize all data to zero.
    constexpr Polynomial(size_t length) noexcept : length(length)
    {
        data = new double[length]{};
        degree_ = -1;
    }

    // Explicit constructor: from coefficient array and degree_
    // make sure to ensure degree is correct
    constexpr explicit Polynomial(const double* coeff, size_t length) noexcept
        : length(length)
    {
        // data = const_cast<double*>(coeff);
        // Don't ask wtf I was doing here pliz.
        //
        data = new double[length];
        for (size_t i = 0; i < length; ++i)
            data[i] = coeff[i];

        update_degree();
    }

    //initialize Polynomial from the list
    //init.size() will yield the number of elements in init.
    constexpr explicit Polynomial(const std::initializer_list<double>& init) noexcept
    {
        length = init.size(); //keep
        // data = (double*)init.begin();

        data = new double[length];
        for (size_t i = 0; i < length; ++i)
            data[i] = *(init.begin() + i);

        update_degree();
    }

    // ***************** Rule of 5
    //copy constructor
    constexpr Polynomial(const Polynomial & rhs) noexcept
        : length(rhs.length), degree_(rhs.degree_)
    {
        data = new double[length];
        for (size_t i = 0; i < length; ++i)
            data[i] = rhs.data[i];
    }

    //move constructor
    constexpr Polynomial(Polynomial&& rhs) noexcept
        : length(std::move(rhs.length)), degree_(std::move(rhs.degree_))
    {
        data = new double[length];
        for (size_t i = 0; i < length; ++i)
            data[i] = rhs.data[i];

        rhs.length = 0;
        rhs.degree_ = -1;

        delete[] rhs.data;
        rhs.data = nullptr;
    }

    //add copy assignment
    constexpr Polynomial operator=(const Polynomial& rhs) noexcept
    {
        length = rhs.length;
        degree_ = rhs.degree_;

        // Realloc with new length
        if (data)
        {
            delete[] data;
            data = new double[length];
        }

        for (size_t i = 0; i < length; ++i)
            data[i] = rhs.data[i];

        return *this;
    }

    //add move assignment
    constexpr Polynomial operator=(Polynomial&& rhs) noexcept
    {
        length = std::move(rhs.length);
        degree_ = std::move(rhs.degree_);

        // Realloc with new length
        if (data)
        {
            delete[] data;
            data = new double[length];
        }

        for (size_t i = 0; i < length; ++i)
            data[i] = rhs.data[i];

        rhs.length = 0;
        rhs.degree_ = -1;

        delete[] rhs.data;
        rhs.data = nullptr;

        return *this;
    }

    //destructor
    constexpr ~Polynomial() noexcept
    {
        if (data)
        {
            delete[] data;
            data = nullptr;
        }
    }

    constexpr double operator[](const size_t power) const noexcept
    {
        if (power > length)
            return 0;

        // for (int i = length; i > 0; --i)
        // {
        //     if (data[--i] != 0.0)
        //     {
        //         degree_ = i;
        //         return;
        //     }
        // }

        return data[power];
    }

    constexpr double& operator[](const size_t power)
    {
        if (power > length)
            throw std::out_of_range("Index out of range!");

        return data[power];
    }

    //Return the result of X = x for e.g.: 1 + x + x^2 + 3x^3
    constexpr double evaluate(double x) const noexcept
    {
        if (degree_ == -1)
            return 0.0;

        double result = data[degree_];
        for (int i = degree_ - 1; i >= 0; --i)
            result = result * x + data[i];

        return result;
    }

    // Addition
    constexpr Polynomial operator+(const Polynomial& other) const noexcept
    {
        size_t minLen = std::min(length, other.length);
        size_t maxLen = std::max(length, other.length);

        Polynomial res(maxLen);
        for (size_t i = 0; i < minLen; ++i)
            res.data[i] = data[i] + other.data[i];

        // Add on remaining
        if (length > other.length)
        {
            for (size_t i = minLen; i < maxLen; ++i)
                res.data[i] = data[i];
        }
        else
        {
            for (size_t i = minLen; i < maxLen; ++i)
                res.data[i] = other.data[i];
        }

        res.update_degree();
        return res;
    }

    // Subtraction
    constexpr Polynomial operator-(const Polynomial& other) const noexcept
    {
        size_t minLen = std::min(length, other.length);
        size_t maxLen = std::max(length, other.length);

        Polynomial res(maxLen);
        for (size_t i = 0; i < minLen; ++i)
            res.data[i] = data[i] - other.data[i];

        // Add on remaining
        if (length > other.length)
        {
            for (size_t i = minLen; i < maxLen; ++i)
                res.data[i] = -data[i];
        }
        else
        {
            for (size_t i = minLen; i < maxLen; ++i)
                res.data[i] = -other.data[i];
        }

        res.update_degree();
        return res;
    }

    // Scalar multiplication
    constexpr Polynomial operator*(double scalar) const noexcept
    {
        Polynomial res(*this);
        for (size_t i = 0; i < length; ++i)
            res.data[i] *= scalar;

        res.update_degree();
        return res;
    }

    //Add the function signature for
    //a = b * c where a, b, c are all polynomials
    /**************/
    constexpr Polynomial operator*(const Polynomial& other) const noexcept
    {
        // Zero polynomial case
        if (degree_ == -1 || other.degree_ == -1) {
            Polynomial result(0);
            return result;
        }

        // Result degree is sum of input degrees
        const int resultDegree = degree_ + other.degree_;
        Polynomial result(resultDegree + 1);  // +1 for array size

        // Multiply each term of this by each term of other
        for (int i = 0; i <= degree_; ++i) {
            for (int j = 0; j <= other.degree_; ++j) {
                int k = i + j;
                auto me = (*this)[i];
                auto that = other[j];
                result.data[k] += me * that;  // Multiply data
            }
        }

        result.update_degree();
        return result;
    }

    // Equality comparison
    constexpr bool operator==(const Polynomial& other) const noexcept
    {
        if ((length != other.length) || (degree_ != other.degree_))
            return false;

        for (size_t i = 0; i < length; ++i)
        {
            if (data[i] != other.data[i])
                return false;
        }

        return true;
    }

}; //Polynomial


} //namespace

//do not alter the code below this line
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


template <>
struct std::formatter<math::Polynomial> {
    constexpr auto parse(std::format_parse_context& ctx) {
        return ctx.begin();
    }

    constexpr auto format(const math::Polynomial& p, std::format_context& ctx) const {
        if (p.degree() == -1) {
            return std::format_to(ctx.out(), "0");
        }

        bool first = true;
        auto out = ctx.out();

        for (int i = 0; i <= p.degree(); ++i) {
            double coeff = p[i];

            if (coeff == 0.0) continue;

            if (!first && coeff > 0) {
                out = std::format_to(out, " + ");
            } else if (!first && coeff < 0) {
                out = std::format_to(out, " - ");
                coeff = -coeff;
            } else if (coeff < 0) {
                out = std::format_to(out, "-");
                coeff = -coeff;
            }

            if (i == 0) {
                out = std::format_to(out, "{}", coeff);
            } else if (coeff == 1.0) {
                out = std::format_to(out, "x");
                if (i > 1) out = std::format_to(out, "^{}", i);
            } else {
                out = std::format_to(out, "{}x", coeff);
                if (i > 1) out = std::format_to(out, "^{}", i);
            }

            first = false;
        }

        return out;
    }
};


namespace math::tests {
    // Test 1: Default construction
    constexpr bool test_default_construction() {
        Polynomial p(0);
        return p.degree() == -1;
    }

    // Test 2: Construction and accessors
    constexpr bool test_construction_length() {
        double coeff[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, 10);
        return p.size() == 10;
    }

    constexpr bool test_construction_degree() {
        double coeff[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, 10);
        return p.degree() == 2;
    }

    constexpr bool test_construction() {
        double coeff[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, 10);
        return p.degree() == 2 &&
               p[0] == 1.0 &&
               p[1] == 2.0 &&
               p[2] == 3.0;
    }

    // Test 3: Evaluation - constant polynomial
    constexpr bool test_evaluate_constant() {
        double coeff[] = {5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, std::size(coeff));
        return p.evaluate(10.0) == 5.0 && p.evaluate(0) == 5.0;
    }

    // Test 4: Evaluation - linear
    constexpr bool test_evaluate_linear() {
        double coeff[] = {1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, std::size(coeff));  // 1 + 2x
        return p.evaluate(3.0) == 7.0;  // 1 + 2*3 = 7
    }

    // Test 5: Evaluation - quadratic
    constexpr bool test_evaluate_quadratic() {
        double coeff[] = {1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, std::size(coeff));  // 1 + x²
        return p.evaluate(2.0) == 5.0;  // 1 + 4 = 5
    }

    // Test 6: Addition
    constexpr bool test_addition() {
        double c1[] = {1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + x
        Polynomial p2(c2, std::size(c2));  // 2 + 3x
        Polynomial sum = p1 + p2;  // Should be 3 + 4x
        auto result = sum[0] == 3.0 && sum[1] == 4.0;
        result &= sum.degree() == 1;
        return result;
    }

        // Test 6: Addition
    constexpr bool test_addition_diff_length() {
        double c1[] = {1.0, 1.0};
        double c2[] = {2.0, 3.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + x
        Polynomial p2(c2, std::size(c2));  // 2 + 3x
        Polynomial sum = p1 + p2;  // Should be 3 + 4x + 2x^2
        auto result = sum[0] == 3.0 && sum[1] == 4.0 && sum[2] == 2.0;
        result &= sum.degree() == 2;
        return result;
    }

    // Test 7: Subtraction
    constexpr bool test_subtraction() {
        double c1[] = {5.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {2.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 5 + 3x
        Polynomial p2(c2, std::size(c2));  // 2 + x
        Polynomial diff = p1 - p2;  // Should be 3 + 2x
        return diff.degree() == 1 &&
               diff[0] == 3.0 &&
               diff[1] == 2.0;
    }

    constexpr bool test_subtraction_diff_length() {
        double c1[] = {1.0, 1.0};
        double c2[] = {2.0, 3.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + x
        Polynomial p2(c2, std::size(c2));  // 2 + 3x + 2x^2
        Polynomial sum = p1 - p2;  // Should be -1 - 2x - 2x^2
        auto result = sum[0] == -1.0 && sum[1] == -2.0 && sum[2] == -2.0;
        result &= sum.degree() == 2;
        return result;
    }

    constexpr bool test_subtraction_const_correctness() {
        double c1[] = {1.0, 1.0};
        double c2[] = {2.0, 3.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        const Polynomial p1(c1, std::size(c1));  // 1 + x
        const Polynomial p2(c2, std::size(c2));  // 2 + 3x + 2x^2
        const Polynomial sum = p1 - p2;  // Should be -1 - 2x - 2x^2
        auto result = sum[0] == -1.0 && sum[1] == -2.0 && sum[2] == -2.0;
        result &= sum.degree() == 2;
        return result;
    }

    // Test 8: Scalar multiplication
    constexpr bool test_scalar_mult() {
        double coeff[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p(coeff, std::size(coeff));  // 1 + 2x + 3x²
        Polynomial scaled = p * 2.0;  // 2 + 4x + 6x²
        return scaled.degree() == 2 &&
               scaled[0] == 2.0 &&
               scaled[1] == 4.0 &&
               scaled[2] == 6.0;
    }

    // Test 9: Polynomial multiplication (simple)
    constexpr bool test_poly_mult_simple() {
        double c1[] = {1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + x
        Polynomial p2(c2, std::size(c2));  // 1 + x
        Polynomial prod = p1 * p2;  // (1 + x)² = 1 + 2x + x²
        return prod.degree() == 2 &&
               prod[0] == 1.0 &&
               prod[1] == 2.0 &&
               prod[2] == 1.0;
    }


    // Test 13: Equality
    constexpr bool test_equality() {
        double c1[] = {1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));
        Polynomial p2(c2, std::size(c2));
        return p1 == p2;
    }

    // Test 14: Evaluate result of addition
    constexpr bool test_eval_after_add() {
        double c1[] = {1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));
        Polynomial p2(c2, std::size(c2));
        Polynomial sum = p1 + p2;  // 2 + 2x
        return sum.evaluate(3.0) == 8.0;  // 2 + 2*3 = 8
    }

    bool test_print() {
        std::string soll = "1 + 2x + 3x^2 - 4x^3";
        std::string ist = std::format("{}", math::Polynomial({1, 2, 3, -4}));
        return 0 == soll.compare(ist);
    }

    constexpr bool copy_constructor_length_correct() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2 = p1;  // Copy constructor
        return p2.size() == p1.size();
    }

    constexpr bool copy_constructor_degree_correct() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2 = p1;  // Copy constructor
        return p2.degree() == p1.degree();
    }

    // Test: Copy constructor
    constexpr bool test_copy_constructor() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2 = p1;  // Copy constructor

        // Check that p2 has same data
        bool same_data = p2.degree() == p1.degree() &&
                        p2[0] == p1[0] &&
                        p2[1] == p1[1] &&
                        p2[2] == p1[2];

        // Check that p2 is independent (different memory)
        // We verify this by ensuring both polynomials still work correctly
        return same_data && p2.degree() == 2;
    }

    constexpr bool test_move_constructor_length() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        const auto length = p1.size();
        Polynomial p2 = std::move(p1);  // Move constructor
        return p2.size() == length;
    }

    constexpr bool test_move_constructor_degree() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        const auto degree = p1.degree();
        Polynomial p2 = std::move(p1);  // Move constructor
        return p2.degree() == degree;
    }

    constexpr bool test_move_constructor_cleanup() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2 = std::move(p1);  // Move constructor
        return p1.degree() == -1 && p1.size() == 0 && p1.has_moved();
    }

    // Test: Move constructor
    constexpr bool test_move_constructor() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2 = std::move(p1);  // Move constructor

        // Check that p2 has the data
        bool has_data = p2.degree() == 2 &&
                       p2[0] == 1.0 &&
                       p2[1] == 2.0 &&
                       p2[2] == 3.0;

        // Check that p1 is emptied (moved-from state)
        bool p1_emptied = p1.degree() == -1;

        return has_data && p1_emptied;
    }

    constexpr bool test_copy_assignment_length() {
        Polynomial p1({1,2,3});
        Polynomial p2({1,2});
        p2 = p1;

        return p1.size() == p2.size();
    }

    // Test: Copy assignment operator
    constexpr bool test_copy_assignment() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {5.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2(c2, std::size(c2));  // 5 + 6x

        p2 = p1;  // Copy assignment

        // Check that p2 now has p1's data
        const bool same_data = p2.degree() == 2 &&
                        p2[0] == 1.0 &&
                        p2[1] == 2.0 &&
                        p2[2] == 3.0;

        // Check that p1 is unchanged
        const bool p1_unchanged = p1.degree() == 2 && p1[0] == 1.0;

        return same_data && p1_unchanged;
    }

    // Test: Move assignment operator

    constexpr bool test_move_assignment_cleanup() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {5.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2(c2, std::size(c2));  // 5 + 6x

        p2 = std::move(p1);  // Move assignment
        // Check that p1 is emptied (moved-from state)
        return p1.degree() == -1 && p1.size() == 0 && p1.has_moved();
    }

    constexpr bool test_move_assignment() {
        double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        double c2[] = {5.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
        Polynomial p2(c2, std::size(c2));  // 5 + 6x

        p2 = std::move(p1);  // Move assignment

        // Check that p2 now has p1's data
        bool has_data = p2.degree() == 2 &&
                       p2[0] == 1.0 &&
                       p2[1] == 2.0 &&
                       p2[2] == 3.0;

        // Check that p1 is emptied (moved-from state)
        bool p1_emptied = p1.degree() == -1;

        return has_data && p1_emptied;
    }

    // Test: Destructor (implicitly tested by scope exit)
    constexpr bool test_destructor() {
        {
            double c1[] = {1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
            Polynomial p1(c1, std::size(c1));  // 1 + 2x + 3x²
            // Destructor called at end of scope
        }
        // If we reach here, destructor didn't crash
        return true;
    }

    constexpr bool test_const_index_operator() {
        const Polynomial p1({1,2,3,4,5});
        for (auto i = 1; i <= 5; i++) {
            if (p1[i-1] != i) { return false; }
        }
        return (p1[6] == 0);
    }

    constexpr bool test_mutable_index_operator() {
        Polynomial p1({1,2,3,4,5});
        for (auto i = 1; i <= 5; i++) {
            p1[i-1] += 1;
        }
        for (auto i = 1; i <= 5; i++) {
            if (p1[i-1] != i + 1) { return false; }
        }
        return true;
    }



}

// Global compile-time assertions
static_assert(math::tests::test_const_index_operator(), "const operator[] does not return correct values");
static_assert(math::tests::test_mutable_index_operator(), "mutable operator[] does give RW access to the data");
static_assert(math::tests::test_destructor(), "destructor does not cleanup properly, or crashes");
static_assert(math::tests::copy_constructor_length_correct(), "copy_constructor gives incorrect length");
static_assert(math::tests::copy_constructor_degree_correct(), "copy_constructor gives incorrect degree");
static_assert(math::tests::test_copy_constructor(), "copy constructor does not copy data over correctly");
static_assert(math::tests::test_move_constructor_length(), "move constructor does not set length correctly");
static_assert(math::tests::test_move_constructor_degree(), "move constructor does not set degree correctly");
static_assert(math::tests::test_move_constructor_cleanup(), "move constructor does perform cleanup correctly");
static_assert(math::tests::test_move_constructor(), "move constructor does not work correctly");
static_assert(math::tests::test_copy_assignment_length(), "copy assignment p1 = p2, does not grow size of p1");
static_assert(math::tests::test_copy_assignment());
static_assert(math::tests::test_move_assignment_cleanup(), "move assignment does not cleanup correctly");
static_assert(math::tests::test_move_assignment(), "move assignment does not work correctly");
static_assert(math::tests::test_default_construction());
static_assert(math::tests::test_construction_length(), "array constructor does not set length correctly");
static_assert(math::tests::test_construction_degree(), "array constructor does not set degree correctly");
static_assert(math::tests::test_construction(), "array constructor does not set data correctly");
static_assert(math::tests::test_evaluate_constant(), "evaluate() handles constant factors incorrectly");
static_assert(math::tests::test_evaluate_linear(), "evaluate() handles linear factors incorrectly");
static_assert(math::tests::test_evaluate_quadratic(), "evaluate() handles quadratic factors incorrectly");
static_assert(math::tests::test_addition(), "operator + does not work correctly");
static_assert(math::tests::test_addition_diff_length(), "operator + does not handle Polynomials of different lengths correctly");
static_assert(math::tests::test_subtraction(), "operator - does not work correctly");
static_assert(math::tests::test_subtraction_diff_length(), "operator - does not handle operands of different lengths");
static_assert(math::tests::test_subtraction_const_correctness(), "operator - does not respect const correctness");
static_assert(math::tests::test_scalar_mult(), "Polynomial * double does not work");
static_assert(math::tests::test_poly_mult_simple(), "Polynomial * Polynomial does not work");
static_assert(math::tests::test_equality(), "operator == does not work");
static_assert(math::tests::test_eval_after_add());

int main() {
    assert(math::tests::test_print());
    std::println("{}", math::Polynomial{1,2,3,-4});
    std::println("{}", studentnumber);
}


