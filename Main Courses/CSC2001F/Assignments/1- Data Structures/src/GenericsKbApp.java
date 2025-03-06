/**
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 05/03/25
 */
public class GenericsKbApp
{
    public enum KnowledgeBaseType
    {
        Array,
        BinarySearchTree
    }

    public GenericsKbApp(String appName, KnowledgeBaseType kbType)
    {
        m_AppName = appName;
        m_KnowledgeBaseType = kbType;
    }

    public void Run()
    {
        Console.WriteLine("--------%s--------", m_AppName);

        while (true)
        {
            String kBPath = (m_KnowledgeBase != null) ? m_KnowledgeBase.GetKnowledgeBasePath() : "";

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


    private void LoadKnowledgeBaseImpl()
    {
        Console.Write("Enter file name: ");
        String fileName = Console.ReadLine();

        try
        {
            switch (m_KnowledgeBaseType)
            {
                case KnowledgeBaseType.Array: m_KnowledgeBase = new KnowledgeBaseArray(fileName); break;
                case KnowledgeBaseType.BinarySearchTree: m_KnowledgeBase = new KnowledgeBaseBST(fileName); break;
            }

            Console.WriteLine("\nKnowledge base loaded successfully.\n");
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }

    private void UpdateStatementImpl()
    {
        Console.Write("Enter the term to update: ");
        String searchTerm = Console.ReadLine();

        Statement st = m_KnowledgeBase.LookupStatement(searchTerm);
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

            if (m_KnowledgeBase.AddStatement(newSt))
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

            if (m_KnowledgeBase.UpdateStatement(st, updatedSt))
                Console.WriteLine("\nStatement updated.\n");
            else
                Console.WriteLine("\nFailed to update statement!\n");
        }
        else
            Console.WriteLine("\nStatement not updated! A statement for the term '%s' already exists with a higher confidence score.\n",
                searchTerm);
    }

    private void SearchByTermImpl()
    {
        Console.Write("Enter the term to search: ");
        String searchTerm = Console.ReadLine();

        Statement e = m_KnowledgeBase.LookupStatement(searchTerm);
        if (e != null)
        {
            Console.WriteLine("\nStatement found: %s (Confidence score: %.2f).\n", e.GetSentence(), e.GetConfidence());
            return;
        }

        Console.WriteLine("\nStatement could not be found!\n");
    }

    private void SearchByTermAndSentenceImpl()
    {
        Console.Write("Enter the term: ");
        String term = Console.ReadLine();

        Console.Write("Enter the statement to search for: ");
        String sentence = Console.ReadLine();

        Statement st = m_KnowledgeBase.LookupStatement(term, sentence);
        if (st != null)
        {
            Console.WriteLine("\nThe statement was found and has a confidence score of %.2f.\n", st.GetConfidence());
            return;
        }

        Console.WriteLine("\nStatement could not be found!\n");
    }

    protected KnowledgeBase m_KnowledgeBase;
    protected String m_AppName;
    protected KnowledgeBaseType m_KnowledgeBaseType;
}
