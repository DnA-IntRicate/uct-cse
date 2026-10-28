import java.util.*;
import java.io.*;

/**
 * This program does something...
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 15/05/25
 */
public class TextEdit
{
    public static void main(String[] args)
    {
        Scanner scanner = new Scanner(System.in);
        Print("Enter the name of the text file:");

        ArrayList<String> lines = new ArrayList<String>();
        try (Scanner fileScanner = new Scanner(new File(scanner.nextLine())))
        {
            while (fileScanner.hasNext())
                lines.add(fileScanner.nextLine());
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        Print("Enter the editing command sequence:");
        String command = scanner.nextLine();

        Process(command, lines);
        scanner.close();
    }

    private static void Process(final String command, final ArrayList<String> lines)
    {
        ArrayList<Integer> uneditedLines = new ArrayList<Integer>();
        ArrayList<String> editedLines = new ArrayList<String>();
        int i = 1;

        for (String line : lines)
        {
            if (IsEditableBy(command, line))
                line = Edit(command, line);
            else
                uneditedLines.add(i);

            editedLines.add(line);
            i++;
        }

        if (!uneditedLines.isEmpty())
        {
            String unmodifiedLineNumbers = "";
            for (final int num : uneditedLines)
                unmodifiedLineNumbers += Integer.toString(num) + ", ";

            unmodifiedLineNumbers = unmodifiedLineNumbers.substring(0, unmodifiedLineNumbers.length() - 2);
            Print("Unmodified line(s): %s.", unmodifiedLineNumbers);
        }

        for (final String editedLine : editedLines)
            Print(editedLine);

        Print("Done");
    }

    private static int Count(final String s, final char c)
    {
        int res = 0;
        for (int i = 0; i < s.length(); ++i)
        {
           if (s.charAt(i) == c)
                res++;
        }

        return res;
    }

    private static boolean IsEditableBy(final String command, final String text)
    {
        if (text.isEmpty())
            return false;

        if (Count(command, 'm') + Count(command, 'd') > text.length())
            return false;

        return true;
    }

    private static String Edit(final String command, final String text)
    {
        // m: move left
        // d: delete
        // i: insert next char

        String res = "";
        int cursorPos = 0;
        int commandPos = 0;

        while (commandPos < command.length())
        {
            switch (command.charAt(commandPos))
            {
                case 'm': res += text.charAt(cursorPos++); break;
                case 'd': cursorPos++; break;
                case 'i': res += command.charAt(++commandPos); break;
            }

            commandPos++;
        }

        if (cursorPos < text.length())
            res += text.substring(cursorPos);

        return res;
    }

    private static void Print(final String fmt, final Object... args)
    {
        System.out.println(String.format(fmt, args));
    }
}
