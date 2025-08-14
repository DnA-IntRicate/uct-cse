#include <string>
#include <iostream>
#include <fstream>
#include <cstdint>

// We must call delete[] on this return value!
static uint8_t* ReadBytes(const std::string& filePath, size_t& outSize) noexcept
{
    std::ifstream in(filePath, std::ios::in | std::ios::binary | std::ios::ate);
    if (in)
    {
        outSize = in.tellg();
        in.seekg(0, std::ios::beg); // We're not worried about error-handling here

        uint8_t* bytes = new uint8_t[outSize];
        in.read((char*)bytes, outSize);
        in.close();

        return bytes;
    }

    return nullptr;
}

static bool ImageCompare(const std::string& image1Path, const std::string& image2Path) noexcept
{
    size_t size1;
    uint8_t* image1 = ReadBytes(image1Path, size1);
    if (!image1)
    {
        std::cerr << "Failed to load image from: \"" << image1Path << "\"\n";
        return false;
    }

    size_t size2;
    uint8_t* image2 = ReadBytes(image2Path, size2);
    if (!image2)
    {
        std::cerr << "Failed to load image from: \"" << image2Path << "\"\n";
        delete[] image1; // Avoid memory leak on early-return

        return false;
    }

    if (size1 != size2)
    {
        std::cout << "Images have differing sizes!\n";
        return false;
    }

    // Compare each and every byte of the 2 images
    bool imagesEqual = true;
    for (size_t i = 0; i < size1; ++i)
    {
        if (image1[i] != image2[i])
        {
            imagesEqual = false;
            break;
        }
    }

    delete[] image1;
    delete[] image2;

    return imagesEqual;
}

int main(int argc, char** argv)
{
    if (argc != 3)
    {
        std::cout << "No arguments provided!\n\n";
        std::cout << "Correct usage:\n";
        std::cout << "make run ARGS=\"<path_image1> <path_image2>\"\n";

        return 0;
    }

    std::string image1Path(argv[1]);
    std::string image2Path(argv[2]);

    std::cout << "Comparing images...\n\n";
    bool imagesEqual = ImageCompare(image1Path, image2Path);

    if (imagesEqual)
        std::cout << "The two images are equal.\n";
    else
        std::cout << "The two images are NOT equal!\n";

    return 0;
}
