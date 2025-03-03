/**
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class ChatGPTLite
{
    public static void main(String[] args)
    {
        while (true)
        {
            Console.WriteLine("Choose an action from the menu:");
            Console.WriteLine("1. Load a knowledge base from a file");
            Console.WriteLine("2. Add a new statement to the knowledge base");
            Console.WriteLine("3. Search for a statement in the knowledge base by term");
            Console.WriteLine("4. Search for a statement in the knowledge base by term and sentence");
            Console.WriteLine("5. Quit");

            int option = Integer.parseInt(Console.ReadLine());
            if (option == 5)
                break;      // Exit application
        }
    }
}
