import java.util.Scanner;

/**
 * Wrapper class around {@link Scanner} and {@link System} meant to resemble the {@code Console} static class in
 * {@code C#} and streamline I/O repetitive I/O operations regarding {@link System#in} and {@link System#out}.
 *
 * This implementation is very barebones as only what was required of this assignment was implemented.
 *
 * @see <a href="https://www.geeksforgeeks.org/console-class-in-c-sharp/">console-class-in-c-sharp</a>
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class Console
{
    /**
     * Delete the default constructor.
     * If only Java allowed the declaration of static classes like C#...
     */
    private Console() { }

    /**
     * Writes a full line of text to {@link System#out}.
     *
     * @param fmt the format string to write
     * @param args the variable-amount arguments to be formatted into the printed string according to the
     * type-specifiers in {@code fmt}
     */
    public static void WriteLine(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    /**
     * Writes text to {@link System#out}. Unlike {@link Console#WriteLine(String, Object...)}, this function does not
     * output a {@code newline} character at the end of the outputted string.
     *
     * @param fmt the format string to write
     * @param args the variable-amount arguments to be formatted into the printed string according to the
     * type-specifiers in {@code fmt}
     */
    public static void Write(String fmt, Object... args)
    {
        System.out.print(String.format(fmt, args));
    }

    /**
     * Polls and reads the next line of user-input from {@link System#in}.
     *
     * @return the next line of user-input as a string
     */
    public static String ReadLine()
    {
        InitScannerIfNull();
        return s_Scanner.nextLine();
    }

    // Initializes the static instance of the scanner if it hasn't yet been created
    private static void InitScannerIfNull()
    {
        if (s_Scanner == null)
            s_Scanner = new Scanner(System.in);

        /*
         * This implementation does not actually delete the Scanner when we're done with it.
         * So we just take the lazy approach here and let the operating system clean it up when the
         * program terminates. :)
         */
    }

    // The scanner for this class
    private static Scanner s_Scanner;
}
