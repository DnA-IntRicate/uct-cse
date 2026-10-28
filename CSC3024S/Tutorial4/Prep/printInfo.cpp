#include <print>
#include <vector>
#include <typeinfo>


template<typename _Ty>
constexpr void printInfo(const _Ty& value)
{
    std::println("type={}, value={}", typeid(_Ty).name(), value);
}

template<typename _Ty>
constexpr void printInfo(const std::vector<_Ty>& vec)
{
    std::println("size={}, elements={}", vec.size(), vec);
}

//Do not alter the code below this line
//**************************************

int main() {
    std::vector<int> vec = {1, 2, 3};
    printInfo(vec);
    //size=3, elements=[1, 2, 3]
        
    const auto num = 42;
    printInfo(num);
    //type=int, value=42
    
    const auto pi = 3.14159;
    printInfo(pi);
    //type=double, value=3.14159; //may print extra digits due to double
    
    return 0;
}
