import java.util.Scanner;
/**
 * The CarParkSim class contains the main car park simulation method.
 * It creates and manipulates the main objects, and handles user I/O.
 *
 * @author Stephan Jamieson and Adam Foflonker (FFLADA001)
 * @version 07/08/2024
 */
public class CarParkSim
{
    public static void main(final String[] args)
    {
        final Scanner keyboard = new Scanner(System.in);

        // Declare variables to store a Clock and a Register object, create the relevant objects and assign them.
        Register register = new Register();
        Clock clock = new Clock(new Time("00:00:00"));

        System.out.println("Car Park Simulator");
        System.out.printf("The current time is %s.\n", clock.examine().toString());
        System.out.println("Commands: advance {minutes}, arrive, depart, quit.");
        System.out.print(">");
        String input = keyboard.next().toLowerCase();
        while (!input.equals("quit"))
        {
            if (input.equals("advance"))
            {
                // Advance the clock, print the current time.
                clock.advance(new Duration(TimeUnit.MINUTE, keyboard.nextInt()));
                System.out.printf("The current time is %s.\n", clock.examine().toString());
            }
            else if (input.equals("arrive"))
            {
                // Create a new ticket, add it to the register, print details of ticket issued.
                Ticket newTicket = new Ticket(clock.examine(), UIDGenerator.makeUID());
                register.add(newTicket);
                System.out.printf("Ticket issued: %s.\n", newTicket.toString());
            }
            else if (input.equals("depart"))
            {
                // Determine if ticket is valid, i.e. in the register.
                // If not, print error message.
                // If yes, retreive it, calculate duration of stay and print it.
                String ticketID = keyboard.next();

                if (!register.contains(ticketID))
                    System.out.println("Invalid ticket ID.");
                else
                {
                    Ticket ticket = register.retrieve(ticketID);
                    System.out.printf("Ticket details: %s.\n", ticket.toString());
                    System.out.printf("Current time: %s.\n", clock.examine().toString());

                    Duration stayDuration = ticket.age(clock.examine());
                    System.out.printf("Duration of stay: %s.\n", Duration.format(stayDuration, TimeUnit.MINUTE));
                }
            }
            else
            {
                System.out.println("That command is not recognised.");
                System.out.println("Commands: advance <minutes>, arrive, depart, quit.");
            }

            System.out.print(">");
            input = keyboard.next().toLowerCase();
        }

        keyboard.close();
        System.out.println("Goodbye.");
    }
}
