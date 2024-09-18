/**
 * Utility class for working with numbers in the {@link CowsAndBulls} class.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 18/09/24
 */
public class NumberUtils
{
    /** Delete the default constructor. */
    private NumberUtils() { };

    /**
     * Returns the amount of digits of common value and position between {@code numberA} and {@code numberB}.
     * Assumes that the numbers are the same length and contain no repeated digits.
     *
     * @param numberA the first number to check
     * @param numberB the second number to check
     * @return the amount of digits matching between {@code numberA} and {@code numberB}
     */
    public static int countMatches(int numberA, int numberB)
    {
        int res = 0;
        int[] numA = toArray(numberA);
        int[] numB = toArray(numberB);

        for (int i = 0; i < numA.length; ++i)
        {
            if (numA[i] == numB[i])
                res++;
        }

        return res;
    }

    /**
     * Returns the amount of digits common between {@code numberA} and {@code numberB}.
     * Assumes that the numbers are the same length and contain no repeated digits.
     *
     * @param numberA the first number to check
     * @param numberB the second number to check
     * @return the amount of digits intersecting between {@code numberA} and {@code numberB}
     */
    public static int countIntersect(int numberA, int numberB)
    {
        int res = 0;
        int[] numA = toArray(numberA);
        int[] numB = toArray(numberB);

        for (int i = 0; i < numA.length; ++i)
        {
            // Linear-search to find if numB contains numA[i]
            for (int j = 0; j < numB.length; ++j)
            {
                if (numA[i] == numB[j])
                {
                    res++;
                    break;
                }
            }
        }

        return res;
    }

    /**
     * Splits the given {@code number} into its individual digits and returns them as an array.
     *
     * @param number the number to split into an array
     * @return an integer array containing the individual digits of {@code number}
     */
    public static int[] toArray(int number)
    {
        if (number == 0)    // The log10 of 0 is undefined
            return new int[] { 0 };

        // The log10 + 1 of all positive integers equals the amount of digits in the number
        int[] reversedDigits = new int[(int)Math.log10(number) + 1];
        for (int i = 0; i < reversedDigits.length; ++i)
        {
            reversedDigits[i] = number % 10;
            number /= 10;
        }

        int[] res = new int[reversedDigits.length];
        for (int i = 0; i < res.length; ++i) // Reverse the previously found array to get the correct result
            res[i] = reversedDigits[reversedDigits.length - i - 1];

        return res;
    }
}
