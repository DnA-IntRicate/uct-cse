import java.util.ArrayList;
import java.util.HashMap;
import java.util.Scanner;
import java.io.File;
import java.io.IOException;

/**
 * Categorizing a list of words into buckets.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class BucketList
{
    public static void main(String[] args)
    {
        Print("Enter the name of the categories file:");

        Scanner input = new Scanner(System.in);
        String filePath = input.nextLine();

        Print("Enter a comma-separated list of words:");
        String[] wordList = input.nextLine().split(",\\s+");
        input.close();

        ArrayList<String> categories = new ArrayList<String>();
        try (Scanner fileScanner = new Scanner(new File(filePath)))
        {
            while (fileScanner.hasNextLine())
                categories.add(fileScanner.nextLine());
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Process(wordList, categories);
        Print("Done");
    }

    /** Returns the string category in {@code categories} that {@code word} matches best */
    private static String Categorize(String word, final ArrayList<String> categories)
    {
        if (categories.isEmpty() || (word.length() == 0))
            return "";

        int idxLongestCategory = -1;
        int longestLength = -1;

        for (int i = 0; i < categories.size(); ++i)
        {
            final String category = categories.get(i);
            if (word.startsWith(category))
            {
                if (category.length() > longestLength)
                {
                    idxLongestCategory = i;
                    longestLength = category.length();
                }
            }
        }

        return (idxLongestCategory != -1) ? categories.get(idxLongestCategory) : "";
    }

    private static void Process(final String[] words, final ArrayList<String> categories)
    {
        Print("Categorised:");

        HashMap<String, ArrayList<String>> categoryWordMap = new HashMap<String, ArrayList<String>>();
        ArrayList<String> uncategorised = new ArrayList<String>();

        for (final String word : words)
        {
            String category = Categorize(word, categories);
            if (category.isEmpty())
            {
                uncategorised.add(word);
                continue;
            }

            var wordList = categoryWordMap.getOrDefault(category, new ArrayList<String>());
            wordList.add(word);
            categoryWordMap.put(category, wordList);
        }

        for (final String category : categories)
        {
            if (!categoryWordMap.containsKey(category))
            {
                Print("%s:", category);
                continue;
            }

            String lineOut = category + ": ";
            for (final String word : categoryWordMap.get(category))
                lineOut += word + ", ";

            lineOut = lineOut.substring(0, lineOut.length() - 2) + ".";
            Print(lineOut);
        }

        if (!uncategorised.isEmpty())
        {
            Print("Uncategorised:");

            String lineOut = "";
            for (final String word : uncategorised)
                lineOut += word + ", ";

            lineOut = lineOut.substring(0, lineOut.length() - 2) + ".";
            Print(lineOut);
        }
    }

    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
