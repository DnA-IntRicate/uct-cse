/**
 * ChatGPT Lite (Lol)
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class GenericsKbArrayApp // TODO: Create base-class GenericsKbAppBehavior
{
    public static void main(String[] args)
    {
        while (true)
        {
            String kBPath = (s_KnowledgeBase != null) ? s_KnowledgeBase.GetKnowledgeBasePath() : "";

            Console.WriteLine("Choose an action from the menu:");
            Console.WriteLine("1. Load a knowledge base from a file");
            Console.WriteLine("2. Update a statement in the knowledge base");
            Console.WriteLine("3. Search for a statement in the knowledge base by term");
            Console.WriteLine("4. Search for a statement in the knowledge base by term and sentence");
            Console.WriteLine("5. Quit");
            Console.Write("%s> ", kBPath);

            int option = Integer.parseInt(Console.ReadLine());
            if (option == 5)
                break;      // Exit application loop

            switch (option)
            {
                case 1: LoadKnowledgeBaseImpl(); break;
                case 2: UpdateEntryImpl(); break;
                case 3: SearchByTermImpl(); break;
                case 4: SearchByTermAndSentenceImpl(); break;
            }
        }

        Console.WriteLine("\nShutting down...");
    }

    private static void LoadKnowledgeBaseImpl()
    {
        Console.Write("Enter file name: ");
        String fileName = Console.ReadLine();

        try
        {
            s_KnowledgeBase = new KnowledgeBaseArray(fileName);
            Console.WriteLine("\nKnowledge base loaded successfully.\n");
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }

    private static void UpdateEntryImpl()
    {
        Console.Write("Enter the term to update: ");
        String searchTerm = Console.ReadLine();

        Entry entry = s_KnowledgeBase.LookupEntry(searchTerm);
        if (entry == null)
        {
            Console.WriteLine("\nSearch term not found! A new statement will now be created for the term '%s'.\n",
                searchTerm);

            Entry newEntry = new Entry();
            newEntry.SetTerm(searchTerm);

            Console.Write("Enter the sentence: ");
            newEntry.SetSentence(Console.ReadLine());

            Console.Write("Enter the confidence score: ");
            newEntry.SetConfidence(Double.parseDouble(Console.ReadLine()));

            if (s_KnowledgeBase.AddEntry(newEntry))
                Console.WriteLine("\nStatement for term '%s' has been added.\n", newEntry.GetTerm());
            else
                Console.WriteLine("\nFailed to add new statement!\n");

            return;
        }

        Console.WriteLine("\nOriginal statement: %s (Confidence score: %.2f)", entry.GetSentence(), entry.GetConfidence());

        Console.Write("Enter the updated sentence: ");
        String newSentence = Console.ReadLine();

        Console.Write("Enter the new confidence score: ");
        double newConfidence = Double.parseDouble(Console.ReadLine());

        if (newConfidence >= entry.GetConfidence())
        {
            Entry updatedEntry = new Entry(entry);
            updatedEntry.SetSentence(newSentence);
            updatedEntry.SetConfidence(newConfidence);

            if (s_KnowledgeBase.UpdateEntry(entry, updatedEntry))
                Console.WriteLine("\nStatement updated.\n");
            else
                Console.WriteLine("\nFailed to update statement!\n");
        }
        else
            Console.WriteLine("\nStatement not updated! A statement for the term '%s' already exists with a higher confidence score.\n",
                searchTerm);
    }

    private static void SearchByTermImpl()
    {
        Console.Write("Enter the term to search: ");
        String searchTerm = Console.ReadLine();

        Entry e = s_KnowledgeBase.LookupEntry(searchTerm);
        if (e != null)
        {
            Console.WriteLine("\nStatement found: %s (Confidence score: %.2f).\n", e.GetSentence(), e.GetConfidence());
            return;
        }

        Console.WriteLine("\nStatement could not be found!\n");
    }

    private static void SearchByTermAndSentenceImpl()
    {
        Console.Write("Enter the term: ");
        String term = Console.ReadLine();

        Console.Write("Enter the statement to search for: ");
        String sentence = Console.ReadLine();

        Entry e = s_KnowledgeBase.LookupEntry(term, sentence);
        if (e != null)
        {
            Console.Write("\nThe statement was found and has a confidence score of %.2f.\n", e.GetConfidence());
            return;
        }

        Console.WriteLine("\nStatement could not be found!\n");
    }

    private static KnowledgeBaseArray s_KnowledgeBase;
}
