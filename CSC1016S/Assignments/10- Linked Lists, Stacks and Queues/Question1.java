import java.util.Scanner;

/**
 * A basic program simulating the operation of an I/O buffer using a linked queue.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 24/10/24
 *
 * @see LinkedQueue
 */
public class Question1
{
    /** Logs messages to System.out. */
    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    public static void main(String[] args)
    {
        LinkedQueue<String> queue = new LinkedQueue<String>();
        try (Scanner scanner = new Scanner(System.in))
        {
            while (true)
            {
                String input = scanner.nextLine();

                if (input.equals("X"))
                    break;
                else if (input.startsWith("O"))
                {
                    if (queue.Empty())
                        Print("Buffer empty");
                    else
                        Print("Data: " + queue.Dequeue());
                }
                else
                    queue.Enqueue(input);
            }
        }
    }
}
