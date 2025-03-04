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
                case 2: UpdateStatementImpl(); break;
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

    private static void UpdateStatementImpl()
    {
        Console.Write("Enter the term to update: ");
        String searchTerm = Console.ReadLine();

        Statement st = s_KnowledgeBase.LookupStatement(searchTerm);
        if (st == null)
        {
            Console.WriteLine("\nSearch term not found! A new statement will now be created for the term '%s'.\n",
                searchTerm);

            Statement newSt = new Statement();
            newSt.SetTerm(searchTerm);

            Console.Write("Enter the sentence: ");
            newSt.SetSentence(Console.ReadLine());

            Console.Write("Enter the confidence score: ");
            newSt.SetConfidence(Double.parseDouble(Console.ReadLine()));

            if (s_KnowledgeBase.AddStatement(newSt))
                Console.WriteLine("\nStatement for term '%s' has been added.\n", newSt.GetTerm());
            else
                Console.WriteLine("\nFailed to add new statement!\n");

            return;
        }

        Console.WriteLine("\nOriginal statement: %s (Confidence score: %.2f).", st.GetSentence(), st.GetConfidence());

        Console.Write("Enter the updated sentence: ");
        String newSentence = Console.ReadLine();

        Console.Write("Enter the new confidence score: ");
        double newConfidence = Double.parseDouble(Console.ReadLine());

        if (newConfidence >= st.GetConfidence())
        {
            Statement updatedSt = new Statement(st);
            updatedSt.SetSentence(newSentence);
            updatedSt.SetConfidence(newConfidence);

            if (s_KnowledgeBase.UpdateStatement(st, updatedSt))
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

        Statement e = s_KnowledgeBase.LookupStatement(searchTerm);
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

        Statement st = s_KnowledgeBase.LookupStatement(term, sentence);
        if (st != null)
        {
            Console.WriteLine("\nThe statement was found and has a confidence score of %.2f.\n", st.GetConfidence());
            return;
        }

        Console.WriteLine("\nStatement could not be found!\n");
    }

    private static KnowledgeBaseArray s_KnowledgeBase;
}
