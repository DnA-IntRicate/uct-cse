import java.util.Scanner;

/**
 * A simple program to identify mismatched brackets in a string.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 24/10/24
 *
 * @see Vector
 * @see Stack
 */
public class Question2
{
    /** Vector of open brackets parallel to BRACKETS_CLOSE. */
    private static final Vector<Character> BRACKETS_OPEN = new Vector<Character>('{', '[', '(', '<');

    /** Vector of closed brackets parallel to BRACKETS_CLOSE. */
    private static final Vector<Character> BRACKETS_CLOSE = new Vector<Character>('}', ']', ')', '>');

    /** Returns whether these two open and close brackets matching. */
    private static boolean MatchBrackets(char open, char close)
    {
        int openIdx = BRACKETS_OPEN.Find(open);
        if (openIdx == -1)
            return false;

        return BRACKETS_CLOSE.Find(close) == openIdx;
    }

    /** Logs messages to System.out. */
    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    public static void main(String[] args)
    {
        System.out.println("Enter a string to test:");

        String input = "";
        try (Scanner scanner = new Scanner(System.in))
        {
            input = scanner.nextLine().replaceAll("\\s+", "");
        }

        Stack<Character> stack = new Stack<Character>();
        boolean errorAtEnd = false;

        for (final char c : input.toCharArray())
        {
            if (BRACKETS_OPEN.Contains(c))
                stack.Push(c);
            else if (BRACKETS_CLOSE.Contains(c))
            {
                if (stack.Empty())
                {
                    Print("error at end: the close bracket '%c' does not have a corresponding opening bracket.", c);
                    errorAtEnd = true;

                    continue;
                }

                char top = stack.Pop();
                if (!MatchBrackets(top, c))
                {
                    Print("error: '%c' does not match with '%c'.", c, top);
                    return;
                }
            }
        }

        if (!errorAtEnd)
        {
            if (stack.Empty())
                Print("The string is correct! There are no mismatched brackets.");
            else
                Print("error at end: opening bracket '%c' remains unclosed.", stack.Top());
        }
    }
}
