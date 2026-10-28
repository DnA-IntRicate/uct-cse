import java.util.Scanner;
import java.util.ArrayList;
import java.util.HashMap;
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

        if (words.size() == 1)
            return "Longest is 1.";

        // Accumulator for storing the longest sub-sequence lengths
        ArrayList<Integer> lengths = new ArrayList<Integer>();
        int subStrLen = 1;

        for (int i = 1; i < words.size(); ++i)
        {
            if (words.get(i - 1).compareToIgnoreCase(words.get(i)) < 0)
                subStrLen++;
            else
            {
                lengths.add(subStrLen);
                subStrLen = 1;
            }
        }

        // Store the last sequence length
        lengths.add(subStrLen);

        if (lengths.isEmpty())
            return "Longest is 1.";

        // Ty1 = SubstringLength, Ty2 = Count
        HashMap<Integer, Integer> lenOccurenceMap = new HashMap<Integer, Integer>();
        int longestSubStr = 0;

        for (int i : lengths)
        {
            longestSubStr = Math.max(i, longestSubStr);
            lenOccurenceMap.put(i, lenOccurenceMap.getOrDefault(i, 0) + 1);
        }

        if (lenOccurenceMap.get(longestSubStr) > 1)
            return String.format("Multiple solutions length %d.", longestSubStr);

        return String.format("Longest is %d.", longestSubStr);
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
