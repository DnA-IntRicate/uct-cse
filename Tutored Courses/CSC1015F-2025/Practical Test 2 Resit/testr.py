# Adam Foflonker

nums = list(map(abs, map(int, input("Enter a comma-separated list of integers:").split(", "))))
pairCount = len([i for i in range(len(nums) - 1) if str(nums[i])[0] == str(nums[i + 1])[0]])
print(f"Number of adjacent pairs of numbers starting with the same digit: {pairCount}.")
