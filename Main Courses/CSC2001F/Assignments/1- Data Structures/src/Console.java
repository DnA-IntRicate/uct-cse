import java.util.Scanner;

/**
 *
 * @author Adam Foflonker (FFLADA001)
 * @verion 03/03/25
 */
public class Console
{
    public static void WriteLine(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    public static String ReadLine()
    {
        InitScannerIfNull();
        return s_Scanner.nextLine();
    }

    private static void InitScannerIfNull()
    {
        if (s_Scanner == null)
            s_Scanner = new Scanner(System.in);
    }

    private static Scanner s_Scanner;
}
