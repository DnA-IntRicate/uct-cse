import java.util.Scanner;
import java.util.ArrayList;

/**
 * Computer details
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Question1
{
    public static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    public static String Input(String prompt)
    {
        if (s_Scanner == null)
            s_Scanner = new Scanner(System.in);

        Print(prompt);
        return s_Scanner.nextLine();
    }

    private static Box AddBoxImpl()
    {
        String serialNumber = Input("Enter the serial number");
        String manufacturer = Input("Enter the manufacturer");
        String color = Input("Enter the colour");
        int memoryMb = Integer.parseInt(Input("Enter the amount of memory (MB)"));

        return new Box(serialNumber, manufacturer, color, memoryMb);
    }

    private static Screen AddScreenImpl()
    {
        String serialNumber = Input("Enter the serial number");
        String manufacturer = Input("Enter the manufacturer");
        String color = Input("Enter the colour");
        int size = Integer.parseInt(Input("Enter the screen size in inches"));

        return new Screen(serialNumber, manufacturer, color, size);
    }

    private static Accessory AddAccessoryImpl()
    {
        String serialNumber = Input("Enter the serial number");
        String manufacturer = Input("Enter the manufacturer");
        String color = Input("Enter the colour");

        return new Accessory(serialNumber, manufacturer, color);
    }

    private static boolean DeleteComponentImpl(ArrayList<Component> components)
    {
        String serialNumber = Input("Enter the serial number");
        for (int i = 0; i < components.size(); ++i)
        {
            if (components.get(i).GetSerialNumber().equals(serialNumber))
            {
                components.remove(i);
                return true;
            }
        }

        return false;
    }

    private static void ListComponentsImpl(final ArrayList<Component> components)
    {
        for (final Component component : components)
            Print(component.toString());
    }

    private static void Cleanup()
    {
        s_Scanner.close();
    }

    public static void main(String[] args)
    {
        Print("Welcome to Great International Technology");

        ArrayList<Component> components = new ArrayList<Component>();
        while (true)
        {
            String menuItem = Input("MENU: add (B)ox, add (S)creen, add (A)ccessories, (D)elete, (L)ist, (Q)uit");
            switch (menuItem.toLowerCase())
            {
                case "b":
                    components.add(AddBoxImpl());
                    Print("Done");
                    break;

                case "s":
                    components.add(AddScreenImpl());
                    Print("Done");
                    break;

                case "a":
                    components.add(AddAccessoryImpl());
                    Print("Done");
                    break;

                case "d":
                    if (DeleteComponentImpl(components))
                        Print("Done");
                    else
                        Print("Not found");
                    break;

                case "l":
                    ListComponentsImpl(components);
                    Print("Done");
                    break;

                case "q":
                    Cleanup();
                    return;
            }
        }
    }

    private static Scanner s_Scanner;
}
