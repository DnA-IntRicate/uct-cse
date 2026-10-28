// Adam Foflonker
// FFLADA001
// 20 August 2026


//compile with the following options
//-std=c++23 -Wall
//earlier C++ versions cannot compile this code.

//do not ignore warnings or errors
//Add all code marked in functions with /**********/ as needed
//to implement the functionality.

//Each function in the dynamic array should have the functionality
//outlined in its top comment.
//You cannot throw exceptions in a noexcept function
//You *must* throw exceptions as needed in any function not marked noexcept

#include <stdexcept>
#include <cassert>
#include <iostream>
#include <algorithm>
#include <cstring>

//students need to fill in the details for all of the member functions
//of DynamicArray, the function signatures are given

template <typename T>
class DynamicArray {
private:
    T* data;
    int current_size;
    int current_capacity;
public:
    // Constructor: Initialize an empty array with default capacity of 16
    constexpr DynamicArray() noexcept : current_size(0), current_capacity(16) 
    {
        data = new T[current_capacity];        
    }

    //Here is how to throw an error
    constexpr void ErrorExample() {
        //do not worry about getting the exception type right
        //out_of_range is fine for everything
        //even if it is *technically* wrong
        throw std::out_of_range("example reason");
    }

    // Constructor: Initialize with a specific initial capacity
    constexpr explicit DynamicArray(const int initial_capacity) noexcept : current_size(0), current_capacity(initial_capacity) 
    {
        data = new T[current_capacity];
    }

    // Destructor: Clean up allocated memory
    constexpr ~DynamicArray() noexcept 
    {
        delete[] data;
        data = nullptr;
    }

    // Get element at index
    // Throws std::out_of_range if index is invalid
    constexpr T get(int index) const 
    {
        if (index >= current_size)
            throw std::out_of_range("Index was out of range!");

        return data[index];
    }


    // Set element at index
    // Throws std::out_of_range if index is invalid
    constexpr void set(int index, const T& value)  
    {
        if (index >= current_size)
            throw std::out_of_range("Index was out of range!");

        data[index] = value;
    }

    // Return the number of elements currently stored
    constexpr auto size() const noexcept { return current_size; }

    // Add an element to the end
    // Automatically doubles capacity if needed
    constexpr void push(const T& value) noexcept 
    {
        if (current_capacity < (current_size + 1))
        {
            current_capacity *= 2;

            // Reallocate the array with a new size and copy content
            T* new_data = new T[current_capacity];

            // memcpy is not constexpr!
            // memcpy(data, new_data, current_size);
            for (int i = 0; i < current_size; ++i)
                new_data[i] = data[i];

            delete[] data;
            data = new_data;
        }

        data[current_size++] = value;
    }

    // Remove and return the last element
    // Throws std::underflow_error if array is empty
    constexpr T pop() 
    {
        if (empty())
            throw std::underflow_error("Array is empty!");

        // T res = std::exchange(data[--current_size], 0);
        T res = data[--current_size];
        data[current_size] = 0;

        return res;
    }

    // Return the currently allocated capacity
    constexpr auto capacity() const noexcept { return current_capacity; }

    // Check if array is empty
    constexpr bool empty() const noexcept { return !data || !current_size || !current_capacity; }

    // Clear all elements (does not deallocate)
    constexpr void clear() noexcept 
    {
        if (empty())
            return;

        // memset is not constexpr!
        // memset(data, 0, current_capacity);
        
        for (int i = 0; i < current_capacity; ++i)
            data[i] = 0;

        current_size = 0;
    }

    //Perform a sanity check of the data, return false if inconsistent 
    constexpr bool is_valid() noexcept { return data; } 
};

/***********************************************************/
//END of student code
//Do NOT touch the code below this line.
//**********************************************************/


// run-time test helper
template <typename Lambda>
constexpr bool exception_triggered(Lambda tester) noexcept {
    try {
        tester(); // Call with invalid arguments that SHOULD throw
        return false;  // If we reach this line, no exception was thrown (Test Fails)
    } catch (...) {
        return true;   // Exception was successfully caught (Test Passes)
    }
}

[[nodiscard]] bool test_exception_raising() {
    return 
      exception_triggered([]{DynamicArray<bool> arr(1); arr.pop(); }) &&
      exception_triggered([]{DynamicArray<bool> arr(1); arr.set(2, false); }) &&
      exception_triggered([]{DynamicArray<bool> arr(1); arr.get(2); }) &&
      !exception_triggered([]{DynamicArray<bool> arr(1); arr.push(true); arr.pop(); });
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
    DynamicArray<int> arr(2);  // Start with capacity 2
    
    int initial_capacity = arr.capacity();
    if (initial_capacity != 2) return false;
    
    arr.push(1);
    arr.push(2);
    // Capacity should still be 2
    if (arr.capacity() != 2) return false;
    
    arr.push(3);  // This exceeds capacity, should double to 4
    if (arr.capacity() != 4) return false;
    if (arr.size() != 3) return false;
    
    arr.push(4);
    // Capacity should still be 4
    if (arr.capacity() != 4) return false;
    
    arr.push(5);  // This exceeds capacity, should double to 8
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
    if (arr.capacity() == 0) return false;  // Capacity should remain
    
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
    DynamicArray<int> arr(1);  // Start with capacity 1
    
    for (int i = 0; i < 100; ++i) {
        arr.push(i);
    }
    
    if (arr.size() != 100) return false;
    if (arr.capacity() < 100) return false;
    
    // Verify all elements are correct
    for (int i = 0; i < 100; ++i) {
        if (arr.get(i) != i) return false;
    }
    
    return true;
}

// Test 8: Clear and reuse
constexpr bool test_clear_and_reuse() {
    DynamicArray<int> arr;
    arr.push(1);
    arr.push(2);
    arr.push(3);
    
    int old_capacity = arr.capacity();
    arr.clear();
    
    if (arr.size() != 0) return false;
    if (arr.capacity() != old_capacity) return false;  // Capacity unchanged
    
    arr.push(100);
    arr.push(200);
    
    if (arr.size() != 2) return false;
    if (arr.get(0) != 100) return false;
    if (arr.get(1) != 200) return false;
    
    return true;
}

// Test 9: Verify capacity progression
constexpr bool test_capacity_progression() {
    DynamicArray<int> arr(1);
    
    arr.push(1);  
    if (arr.capacity() != 1) return false;
    
    arr.push(2);  
    if (arr.capacity() != 2) return false;
    
    arr.push(3);  
    if (arr.capacity() != 4) return false;
    
    arr.push(4);  
    arr.push(5);  
    if (arr.capacity() != 8) return false;
    
    return true & arr.is_valid();
}


// Compile-time assertion tests

static_assert(test_basic_operations(), "Basic operations test failed");
static_assert(test_set_method(), "Set method test failed");
static_assert(test_capacity_doubling(), "Capacity doubling test failed");
static_assert(test_empty(), "Empty check test failed");
static_assert(test_clear(), "Clear method test failed");
static_assert(test_multiple_operations(), "Multiple operations test failed");
static_assert(test_large_growth(), "Large growth test failed");
static_assert(test_clear_and_reuse(), "Clear and reuse test failed");
static_assert(test_capacity_progression(), "Capacity progression test failed");

// ============================================================================
// END OF STATIC ASSERTIONS
// ============================================================================


int main() {
    assert(test_exception_raising() && "Test exceptions");
    std::cout << "All tests pass\n";
}
