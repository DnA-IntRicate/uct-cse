#include <concepts>
#include <string>
#include <print>

// Java-like interface: Objects that can produce sound.
// Implementing types must provide:
//   - sound() -> returns a string representing the sound
//   - volume() -> returns an int 

/**********************************************/
//specify the concept here
//BabyLion should pass
//SilentLion should not

template<typename T>
concept Soundable = requires(T value)
{
    { value.sound() } -> std::convertible_to<std::string>;
    { value.volume() } -> std::same_as<int>;
};

/**********************************************/


//###########################################
//do not change the code below this line

class BabyLion {
public:
    auto sound() const { return "Roarish"; }
    auto volume() const { return 6; } 
};

class SilentLion {
    auto silence() { return ""; }
    auto volume() const { return 0; }
};

// Helper function: make any Soundable object "speak"
template<Soundable S>
void makeSound(const S& creature) {
    std::println("{}", creature.sound());
    std::println("Volume: {}/10\n", creature.volume());
}

int main() {
    BabyLion diavoletto;
    makeSound(diavoletto);   
}