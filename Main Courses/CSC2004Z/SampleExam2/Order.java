import java.util.Scanner;
import java.util.ArrayList;
import java.io.File;
import java.io.IOException;

/**
 * Determines the longest sub-sequence of a sentence where the words are in alphabetical order.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 22/02/25
 */
public class Order
{
    public static void main(String[] args)
    {
        Print("Enter the name of the word lists text file:");

        Scanner input = new Scanner(System.in);
        String filePath = input.nextLine();
        input.close();

        try (Scanner fileScanner = new Scanner(new File(filePath)))
        {
            while (fileScanner.hasNextLine())
                Print(Process(fileScanner.nextLine()));
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Print("Done");
    }

    /** Determines the longest sub-sequence of a sentence where the words are in alphabetical order. */
    private static String Process(String line)
    {
        ArrayList<String> words = new ArrayList<String>();
        try (Scanner scanner = new Scanner(line))
        {
            scanner.useDelimiter(" ");

            while (scanner.hasNext())
                words.add(scanner.next());
        }

        // Accumulator for storing the longest sub-sequence lengths
        ArrayList<Integer> longestLengths = new ArrayList<Integer>();
        int subStrLen = 1;
        int longestSubStr = 1;

        for (int i = 1; i < words.size(); ++i)
        {
            if (words.get(i - 1).compareToIgnoreCase(words.get(i)) < 0)
                subStrLen++;
            else if (subStrLen >= longestSubStr)
            {
                longestSubStr = subStrLen;
                subStrLen = 1;
                longestLengths.add(longestSubStr);
            }
        }

        // Account for the value of subStrLen after the loop has ended
        if (subStrLen >= longestSubStr)
        {
            longestSubStr = subStrLen;
            longestLengths.add(longestSubStr);
        }

        // Check if there are multiple longest sub-sequences
        int count = 0;
        for (int i : longestLengths)
        {
            if (i == longestSubStr)
                count++;
        }

        if (count > 1)
            return String.format("Multiple solutions length %d.", longestSubStr);

        return String.format("Longest is %d.", longestSubStr);
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
