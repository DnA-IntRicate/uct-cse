import java.util.Scanner;
import java.util.ArrayList;

/**
 * A simple program to store and manage the details of computer components.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Component
 * @see Accessory
 * @see Box
 * @see Screen
 */
public class Question1
{
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

    // Helper function for printing messages to System.out, Python style.
    private static void Print(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    // Helper function for reading user input from System.in, Python style.
    private static String Input(String prompt)
    {
        // Create the scanner if this function is being called for the first time.
        if (s_Scanner == null)
            s_Scanner = new Scanner(System.in);

        Print(prompt);
        return s_Scanner.nextLine();
    }

    // Implementation for adding a new box.
    private static Box AddBoxImpl()
    {
        String serialNumber = Input("Enter the serial number");
        String manufacturer = Input("Enter the manufacturer");
        String color = Input("Enter the colour");
        int memoryMb = Integer.parseInt(Input("Enter the amount of memory (MB)"));

        return new Box(serialNumber, manufacturer, color, memoryMb);
    }

    // Implementation for adding a new screen.
    private static Screen AddScreenImpl()
    {
        String serialNumber = Input("Enter the serial number");
        String manufacturer = Input("Enter the manufacturer");
        String color = Input("Enter the colour");
        int size = Integer.parseInt(Input("Enter the screen size in inches"));

        return new Screen(serialNumber, manufacturer, color, size);
    }

    // Implementation for adding a new accessory.
    private static Accessory AddAccessoryImpl()
    {
        String serialNumber = Input("Enter the serial number");
        String manufacturer = Input("Enter the manufacturer");
        String color = Input("Enter the colour");

        return new Accessory(serialNumber, manufacturer, color);
    }

    // Implementation for deleting a component.
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

    // Implementation for listing all components.
    private static void ListComponentsImpl(final ArrayList<Component> components)
    {
        for (final Component component : components)
            Print(component.toString());
    }

    // Cleanup program resources before closing.
    private static void Cleanup()
    {
        s_Scanner.close();
    }

    // This program's scanner.
    private static Scanner s_Scanner;
}
