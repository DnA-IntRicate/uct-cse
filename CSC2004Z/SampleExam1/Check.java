import java.io.File;
import java.io.IOException;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.HashSet;

/**
 * This class does... Something.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 20/02/25
 */
public class Check
{
    public static boolean AllCardsEqual(final ArrayList<Card> cards)
    {
        if (cards.isEmpty())
            return false;

        Card prev = cards.get(0);
        for (int i = 1; i < cards.size(); ++i)
        {
            if (!cards.get(i).equals(prev))
                return false;

            prev = cards.get(i);
        }

        return true;
    }

    public static boolean AllCardsDistinct(final ArrayList<Card> cards)
    {
        HashSet<String> cardShapes = new HashSet<String>();
        HashSet<String> cardColors = new HashSet<String>();
        HashSet<String> cardPatterns = new HashSet<String>();

        for (final Card c : cards)
        {
            if (!cardShapes.add(c.GetShape()))
                return false;

            if (!cardColors.add(c.GetColor()))
                return false;

            if (!cardPatterns.add(c.GetPattern()))
                return false;
        }

        return true;
    }

    public static boolean ValidateCardEntries(final String cardEntries)
    {
        // This implementation assumes we don't know how many cards are present in a single entry
        ArrayList<Card> cards = new ArrayList<Card>();
        try (Scanner scanner = new Scanner(cardEntries))
        {
            scanner.useDelimiter(" ");
            while (scanner.hasNext())
                cards.add(new Card(scanner.next()));
        }

        return AllCardsEqual(cards) ^ AllCardsDistinct(cards);
    }

    public static void main(String[] args)
    {
        Print("Enter the name of the cards file:");

        Scanner input = new Scanner(System.in);
        String cardsFilePath = input.nextLine();

        try (Scanner scanner = new Scanner(new File(cardsFilePath)))
        {
            while (scanner.hasNextLine())
            {
                String entries = scanner.nextLine();
                Print("Processing: %s", entries);
                Print(ValidateCardEntries(entries) ? "Valid" : "Invalid");
            }
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Print("Done");
        input.close();
    }

    private static void Print(final String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
