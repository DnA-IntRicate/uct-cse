import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * The entry-point for this assignment. Allows for an instrumented version of the app to be executed if the
 * flag {@code "1"} is passed to the program as a command-line argument.
 *
 * @see Statement
 * @see KnowledgeBase
 * @see KnowledgeBaseAVLTree
 * @see InstrumentationCounter
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 22/03/25
 */
public class GenericsKbAVLApp
{
    /**
     * The main function
     *
     * @param args command-line arguments
     */
    public static void main(String[] args)
    {
        if (args.length > 0)
            InstrumentationCounter.SetEnabled(args[0].equals("1"));

        Console.WriteLine("--------GenericsKbAVLApp%s--------", InstrumentationCounter.IsEnabled() ? "_Instrumented" : "");

        LoadKnowledgeBaseImpl();
        QueryKnowledgeBaseImpl();

        if (InstrumentationCounter.IsEnabled())
        {
            int inserts = InstrumentationCounter.GetInsertCompCount();
            int searches = InstrumentationCounter.GetSearchCompCount();

            Console.WriteLine("Number of comparisons while inserting: %d.", inserts);
            Console.WriteLine("Number of comparisons while searching: %d.", searches);
            Console.WriteLine("Total comparisons: %d.\n", inserts + searches);
        }
    }

    /**
     * Delete the default constructor.
     * If only Java allowed the declaration of static classes like C#...
     */
    private GenericsKbAVLApp() { }

    // Load knowledge base
    private static void LoadKnowledgeBaseImpl()
    {
        String fileName;
        while (true)
        {
            Console.Write("Enter knowledge base path: ");
            fileName = Console.ReadLine();

            if ((new File(fileName)).exists())
                break;

            Console.WriteLine("\nFile does not exist, please enter a valid file name!\n");
        }

        try
        {
            s_KnowledgeBase = new KnowledgeBaseAVLTree(fileName);
            Console.WriteLine("\nKnowledge base loaded successfully.\n");
        }
        catch (Exception e)
        {
            Console.WriteLine("Failed to load knowledge base!");
            e.printStackTrace();
        }
    }

    // Query the knowledge base from a textfile of queries
    private static void QueryKnowledgeBaseImpl()
    {
        String fileName;
        while (true)
        {
            Console.Write("Enter query file path: ");
            fileName = Console.ReadLine();

            if ((new File(fileName)).exists())
                break;

            Console.WriteLine("\nFile does not exist, please enter a valid file name!\n");
        }

        Console.WriteLine("\nQuerying knowledge base from file: '%s'...\n", fileName);

        try
        {
            for (String term : Files.readAllLines(Paths.get(fileName)))
            {
                if (term == null)
                    break;

                Statement st = s_KnowledgeBase.LookupStatement(term);
                if (st == null)
                {
                    Console.WriteLine("Term not found: %s.", term);
                    continue;
                }

                Console.WriteLine("%s: %s (%.1f)", st.GetTerm(), st.GetSentence(), st.GetConfidence());
            }

            Console.WriteLine("\nDone.\n");
        }
        catch (IOException e)
        {
            Console.WriteLine("Failed to load knowledge base queries!");
            e.printStackTrace();
        }
        catch (Exception e)
        {
            Console.WriteLine("\nError querying knowledge base!\n");
            e.printStackTrace();
        }
    }

    /** The app's KnowledgeBase. */
    static KnowledgeBase s_KnowledgeBase;
}
