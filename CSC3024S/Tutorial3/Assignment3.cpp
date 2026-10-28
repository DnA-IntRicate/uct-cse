// Adam Foflonker
// FFLADA001
// 27 Aug 2026

//Compile this with the following options
//-std=c++23 -fsanitize=leak -Wall
//do not ignore warnings and errrors

//Replace all instances of /********/ with the appropriate code to implement the functionality of the DynamicArray class.
//Do the same for the NonMovableDynamicArray class.
//There is no need to add any additional member variables or methods to either class.
//Currently there are 18 errors in the code, after you have completed the implementation there should be 0 errors and 0 warnings.

// NOTE(Adam): There are some signedness issues in set() and push() that throw warnings at compile time,
//             these errors can be bypassed with '-Wno-sign-compare' (fix without modifying the given code).
//             I however, did not do this, since the comments above stated to use '-Wall.'
//             Instead I fixed the warnings (and added comments). I did NOT 'fix' any code below line 223.

#include <stdexcept>
#include <cassert>
#include <print>

//students need to fill in the details for all of the member functions
//of DynamicArray, the function signatures are given
template <typename T>
class DynamicArray {
    //Member variables now declared in the correct order
    size_t current_capacity;
    size_t current_size;
    T* data;
public:
    //We already have a default constructor and a destructor, but we need to declare the
    //other 4 special member functions: 
    // copy constructor, 
    // copy assignment operator
    // move constructor
    // move assignment operator

    // Declare the copy constructor
    // you can declare either an initializer list or a body for the constructor
    // try and make you code DRY and reuse the existing code as much as possible
    constexpr DynamicArray(const DynamicArray &other)
        : current_capacity(other.current_capacity), 
          current_size(other.current_size), 
          data(new T[other.current_capacity])
    {
        std::copy(other.data, other.data + other.current_size, data);
    }

    //Declare the copy assignment operator
    constexpr DynamicArray& operator=(const DynamicArray& rhs)
    {
        if (this == &rhs)
            return *this;

        if (current_capacity != rhs.current_capacity)
        {
            delete[] data;
            data = new T[rhs.current_capacity];
            current_capacity = rhs.current_capacity;
        }

        current_size = rhs.current_size;
        std::copy(rhs.data, rhs.data + rhs.current_size, data);

        return *this;
    }

    //Declare the move constructor
    constexpr DynamicArray(DynamicArray &&rhs) noexcept
        : current_capacity(rhs.current_capacity),
          current_size(rhs.current_size),
          data(rhs.data)
    {
        rhs.current_capacity = 0;
        rhs.current_size = 0;
        rhs.data = nullptr;
    }

    //Declare the move assignment operator
    constexpr DynamicArray& operator=(DynamicArray&& rhs) noexcept
    {
        if (this == &rhs)
            return *this;

        delete[] data;

        current_capacity = rhs.current_capacity;
        current_size = rhs.current_size;
        data = rhs.data;

        rhs.current_capacity = 0;
        rhs.current_size = 0;
        rhs.data = nullptr;

        return *this;
    }

    // Constructor: Initialize an empty array with default capacity of 16
    constexpr DynamicArray() noexcept
    //DRY: delegate construction to specialised constructor
    : DynamicArray(16) {} 

    //Here is how to throw an error
    constexpr void ErrorExample() {
        throw std::out_of_range("example reason");
    }

    // Constructor: Initialize with a specific initial capacity
    constexpr explicit DynamicArray(const int initial_capacity) noexcept
    : current_capacity(initial_capacity), current_size(0) {
        if (0 == current_capacity) { current_capacity = 10; }
        data = new T[current_capacity];
    }

    // Destructor: Clean up allocated memory
    constexpr ~DynamicArray() noexcept {
        delete[] data;
    }

    // Get element at index
    // Throws std::out_of_range if index is invalid
    // Try to make parameters const
    [[nodiscard]] constexpr T get(const size_t index) const {
        if (index >= current_size) {
            throw std::out_of_range("Index out of range in DynamicArray::get()");
        }
        return data[index];
    }

    // Set element at index
    // Throws std::out_of_range if index is invalid
    constexpr void set(int index, const T& value) {
        // NOTE(Adam): Explicitly casted index to size_t before comparison (-Wsign-compare)
        if ((size_t)index < current_size) {
            data[index] = value;
        } else {
            throw std::out_of_range("Index out of range in DynamicArray::set()");
        }
    }

    // Return the number of elements currently stored
    [[nodiscard]] constexpr auto size() const noexcept {
        return current_size;
    }

    // Add an element to the end
    // Automatically doubles capacity if needed
    constexpr void push(const T& value) noexcept {
        if (current_size == current_capacity) { // Double the capacity
            current_capacity *= 2;
            auto new_data = new T[current_capacity];
    // Copy existing elements
            for (size_t i = 0; i < current_size; ++i) // NOTE(Adam): Changed auto to size_t (-Wsign-compare)
                new_data[i] = data[i];
    // Deallocate old array
            delete[] data;
    // Update pointers and capacity
            data = new_data;
        } //if doubling needed
        data[current_size++] = value;
    }

    // Remove and return the last element
    // Throws std::underflow_error if array is empty
    constexpr T pop() {
        if (current_size == 0) {
            throw std::underflow_error("Cannot pop from empty DynamicArray");
        }
        return data[--current_size];
    }

    // Return the currently allocated capacity
    [[nodiscard]] constexpr auto capacity() const noexcept {
        return current_capacity;
    }

    // Check if array is empty
    [[nodiscard]] constexpr bool empty() const noexcept {
        return 0 == current_size;
    }

    // Clear all elements (does not deallocate)
    constexpr void clear() noexcept {
        current_size = 0;
    }

    //Perform a sanity check of the data, return false if inconsistent
    [[nodiscard]] constexpr bool is_valid() noexcept {
        return (current_capacity > 0)
            && (current_size <= current_capacity) 
            && (data != nullptr);
    } 

    [[nodiscard]] constexpr bool has_moved() const noexcept {
        return nullptr == data 
            && 0 == current_size 
            && 0 == current_capacity;
    }

    [[nodiscard]] constexpr T* get_data_for_testing() const noexcept {
        return data;
    }

}; //DynamicArray

template <typename T>
class NonMovableDynamicArray : public DynamicArray<T> {
public:
    //reuse the constructors and destructor from DynamicArray
    constexpr NonMovableDynamicArray() = default;
    constexpr NonMovableDynamicArray(const NonMovableDynamicArray& rhs) = default;
    constexpr ~NonMovableDynamicArray() = default;

    //reuse the copy assignment operator from DynamicArray
    constexpr NonMovableDynamicArray& operator=(const NonMovableDynamicArray& rhs) = default;

    //disable the move constructor and move assignment operator
    NonMovableDynamicArray(NonMovableDynamicArray&&) = delete;
    NonMovableDynamicArray& operator=(NonMovableDynamicArray&&) = delete;
};

//DO NOT MODIFY ANY OF THE CODE BELOW 

// run-time test helper
template <typename Lambda>
[[nodiscard]] constexpr bool exception_triggered(Lambda tester) noexcept {
    try {
        tester(); // Call with invalid arguments that SHOULD throw
        return false; // If we reach this line, no exception was thrown (Test Fails)
    } catch (...) {
        return true; // Exception was successfully caught (Test Passes)
    }
}

[[nodiscard]] bool test_exception_raising() {
    return exception_triggered([]{DynamicArray<bool> arr(1); arr.pop(); }) 
        && exception_triggered([]{DynamicArray<bool> arr(1); arr.set(2, false); }) 
        && exception_triggered([]{DynamicArray<bool> arr(1); [[maybe_unused]] auto x = arr.get(2); }) 
        && !exception_triggered([]{DynamicArray<bool> arr(1); arr.push(true); arr.pop(); });
}

// ============================================================================
// STATIC ASSERTIONS - Compile-time unit tests of the DynamicArray
// ============================================================================

// Test 1: Basic instantiation and push/pop
constexpr bool test_basic_operations() {
    DynamicArray<int> arr;
    arr.push(10);
    arr.push(20);
    arr.push(30);

    if (arr.size() != 3) return false;
    if (arr.get(0) != 10) return false;
    if (arr.get(1) != 20) return false;
    if (arr.get(2) != 30) return false;

    int popped = arr.pop();
    if (popped != 30) return false;
    if (arr.size() != 2) return false;

    return true;
}

// Test 2: Set method
constexpr bool test_set_method() {
    DynamicArray<int> arr;
    arr.push(5);
    arr.push(10);
    arr.push(15);

    arr.set(1, 99);
    if (arr.get(1) != 99) return false;

    return true;
}

// Test 3: Capacity doubling
constexpr bool test_capacity_doubling() {
    DynamicArray<int> arr(2); // Start with capacity 2

    int initial_capacity = arr.capacity();
    if (initial_capacity != 2) return false;

    arr.push(1);
    arr.push(2);
    // Capacity should still be 2
    if (arr.capacity() != 2) return false;

    arr.push(3); // This exceeds capacity, should double to 4
    if (arr.capacity() != 4) return false;
    if (arr.size() != 3) return false;

    arr.push(4);
    // Capacity should still be 4
    if (arr.capacity() != 4) return false;

    arr.push(5); // This exceeds capacity, should double to 8
    if (arr.capacity() != 8) return false;
    if (arr.size() != 5) return false;

    return true;
}

// Test 4: Empty check
constexpr bool test_empty() {
    DynamicArray<int> arr;

    if (!arr.empty()) return false;

    arr.push(42);
    if (arr.empty()) return false;

    arr.pop();
    if (!arr.empty()) return false;

    return true;
}

// Test 5: Clear method
constexpr bool test_clear() {
    DynamicArray<int> arr;
    arr.push(1);
    arr.push(2);
    arr.push(3);

    if (arr.size() != 3) return false;

    arr.clear();
    if (arr.size() != 0) return false;
    if (!arr.empty()) return false;
    if (arr.capacity() == 0) return false; // Capacity should remain

    return true;
}

// Test 6: Multiple operations with different type
constexpr bool test_multiple_operations() {
    DynamicArray<double> arr;

    arr.push(1.5);
    arr.push(2.5);
    arr.push(3.5);
    arr.push(4.5);

    arr.set(2, 10.0);
    if (arr.get(2) != 10.0) return false;

    double val = arr.pop();
    if (val != 4.5) return false;

    if (arr.size() != 3) return false;

    return true;
}

// Test 7: Large capacity growth
constexpr bool test_large_growth() {
    DynamicArray<int> arr(1); // Start with capacity 1

    for (int i = 0; i < 100; ++i) {
        arr.push(i);
    }

    if (arr.size() != 100) { return false; }
    if (arr.capacity() < 100) { return false; }

    // Verify all elements are correct
    for (int i = 0; i < 100; ++i) {
        if (arr.get(i) != i) { return false; }
    }
    return true;
}

// Test 8: Clear and reuse
constexpr bool test_clear_and_reuse() {
    DynamicArray<int> arr;
    arr.push(1);
    arr.push(2);
    arr.push(3);

    // NOTE(Adam): This should be a size_t (causes -Wsign-compare 4 lines below)
    int old_capacity = arr.capacity();
    arr.clear();

    if (arr.size() != 0) { return false; }
    if (arr.capacity() != old_capacity) { return false; } // Capacity unchanged

    arr.push(100);
    arr.push(200);

    if (arr.size() != 2) { return false; }
    if (arr.get(0) != 100) { return false; }
    if (arr.get(1) != 200) { return false; }

    return true;
}

// Test 9: Verify capacity progression
constexpr bool test_capacity_progression() {
    DynamicArray<int> arr(1);

    arr.push(1); 
    if (arr.capacity() != 1) { return false; }

    arr.push(2); 
    if (arr.capacity() != 2) { return false; }

    arr.push(3); 
    if (arr.capacity() != 4) { return false; }

    arr.push(4); 
    arr.push(5); 
    if (arr.capacity() != 8) { return false; }

    return true & arr.is_valid();
}

//Add a constexpr unit test to verify that the copy constructor and copy assignment operator work correctly.
constexpr bool test_copy_constructor() {
    DynamicArray<int> arr1;
    arr1.push(10);
    arr1.push(20);

    // Test copy constructor
    DynamicArray<int> arr2(arr1);
    if (arr2.size() != arr1.size()) return false;
    if (arr2.get(0) != arr1.get(0)) return false;
    if (arr2.get(1) != arr1.get(1)) return false;

    return true;
}

constexpr bool test_copy_assignment() {
    DynamicArray<int> arr1;
    arr1.push(10);
    arr1.push(20);

    // Test copy assignment operator
    DynamicArray<int> arr3;
    arr3 = arr1;
    if (arr3.size() != arr1.size()) return false;
    if (arr3.get(0) != arr1.get(0)) return false;
    if (arr3.get(1) != arr1.get(1)) return false;

    return true;
}


//Add a constexpr unit test to verify that the move constructor and move assignment operator work correctly.
constexpr bool test_move_constructor() {
    DynamicArray<int> arr1;
    arr1.push(10);
    arr1.push(20);      

    // Test move constructor
    DynamicArray<int> arr2(std::move(arr1));
    if (arr2.size() != 2) { return false; }
    if (arr2.get(0) != 10) { return false; }
    if (arr2.get(1) != 20) { return false; }
    if (arr1.size() != 0) { return false; } // arr1 should be in a valid but empty state after move
    if (arr1.capacity() != 0) { return false; } // arr1's capacity should be 0 after move
    if (arr1.get_data_for_testing() != nullptr) { return false; } // arr1's data pointer should be nullptr after move
    if (!arr1.has_moved()) { return false; } // arr1 should indicate it has been moved from
    return true;
}

constexpr bool test_move_assignment() {
    DynamicArray<int> arr1;
    arr1.push(10);
    arr1.push(20);      

    // Test move assignment operator
    DynamicArray<int> arr2;
    arr2 = std::move(arr1);
    if (arr2.size() != 2) { return false; }
    if (arr2.get(0) != 10) { return false; }
    if (arr2.get(1) != 20) { return false; }
    if (arr1.size() != 0) { return false; } // arr1 should be in a valid but empty state after move
    if (arr1.capacity() != 0) { return false; } // arr1's capacity should be 0 after move
    if (arr1.get_data_for_testing() != nullptr) { return false; } // arr1's data pointer should be nullptr after move
    if (!arr1.has_moved()) { return false; } // arr1 should indicate it has been moved from
    return true;
}

constexpr bool test_copy_and_move_combined() {

    if constexpr (!std::is_copy_assignable_v<DynamicArray<int>>) { return false; }// Copy assignment operator is not available
    if constexpr (!std::is_copy_constructible_v<DynamicArray<int>>) { return false; }// Copy constructor is not available
    if constexpr (!std::is_move_assignable_v<DynamicArray<int>>) { return false; }// Move assignment operator is not available
    if constexpr (!std::is_move_constructible_v<DynamicArray<int>>) { return false; }// Move constructor is not available   

    return true;
}

constexpr bool test_non_movable() {
    if constexpr (!std::is_copy_assignable_v<NonMovableDynamicArray<int>>) { return false; }// Copy assignment operator is not available
    if constexpr (!std::is_copy_constructible_v<NonMovableDynamicArray<int>>) { return false; }// Copy constructor is not available
    if constexpr (std::is_move_assignable_v<NonMovableDynamicArray<int>>) { return false; }// Move assignment operator should not be available
    if constexpr (std::is_move_constructible_v<NonMovableDynamicArray<int>>) { return false; }// Move constructor should not be available       

    return true; // If it compiles, the test passes
}

// Compile-time assertion tests
static_assert(test_basic_operations(), "1: Basic operations test failed");
static_assert(test_set_method(), "2: Set method test failed");
static_assert(test_capacity_doubling(), "3: Capacity doubling test failed");
static_assert(test_empty(), "4: Empty check test failed");
static_assert(test_clear(), "5: Clear method test failed");
static_assert(test_multiple_operations(), "6: Multiple operations test failed");
static_assert(test_large_growth(), "7: Large growth test failed");
static_assert(test_clear_and_reuse(), "8: Clear and reuse test failed");
static_assert(test_capacity_progression(), "9: Capacity progression test failed");

//special member functions tests
static_assert(test_copy_constructor(), "10: Copy constructor test failed");
static_assert(test_copy_assignment(), "11: Copy assignment test failed");
static_assert(test_move_constructor(), "12: Move constructor test failed");
static_assert(test_move_assignment(), "13: Move assignment test failed");
static_assert(test_copy_and_move_combined(), "14: Copy and Move combined test failed");
static_assert(test_non_movable(), "15: NonMovableDynamicArray test failed");

// ============================================================================
// END OF STATIC ASSERTIONS
// ============================================================================

int main() {
  assert(test_exception_raising() && "Test exceptions");
  std::println("All tests passed");
}
