import java.util.Scanner;

/**
 * The CarParkSim class contains the main car park simulation method.
 * It creates and manipulates the main objects, and handles user I/O.
 *
 * @author Stephan Jamieson
 * @author Adam Foflonker (FFLADA001)
 * @version 14/08/2024
 */
public class CarParkSim
{
    public static void main(final String[] args)
    {
        final Scanner keyboard = new Scanner(System.in);

        // Declare variables to store a Clock and a Register object, create the relevant objects and assign them.
        Register register = new Register();
        Clock clock = new Clock(new Time("00:00:00"));

        final Currency RAND = new Currency("R", "ZAR", 100);
        TariffTable tariffs = new TariffTable(10);

        // [0 minutes .. 30 minutes] : R10.00
        tariffs.addTariff(new TimePeriod(new Duration(0), new Duration(TimeUnit.MINUTE, 30)),
            new Money("R10.00", RAND));

        // [30 minutes .. 1 hour] : R15.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.MINUTE, 30), new Duration(TimeUnit.HOUR, 1)),
            new Money("R15.00", RAND));

        // [1 hour .. 3 hours] : R20.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 1), new Duration(TimeUnit.HOUR, 3)),
            new Money("R20.00", RAND));

        // [3 hours .. 4 hours] : R30.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 3), new Duration(TimeUnit.HOUR, 4)),
            new Money("R30.00", RAND));

        // [4 hours .. 5 hours] : R40.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 4), new Duration(TimeUnit.HOUR, 5)),
            new Money("R40.00", RAND));

        // [5 hours .. 6 hours] : R50.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 5), new Duration(TimeUnit.HOUR, 6)),
            new Money("R50.00", RAND));

        // [6 hours .. 8 hours] : R60.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 6), new Duration(TimeUnit.HOUR, 8)),
            new Money("R60.00", RAND));

        // [8 hours .. 10 hours] : R70.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 8), new Duration(TimeUnit.HOUR, 10)),
            new Money("R70.00", RAND));

        // [10 hours .. 12 hours] : R90.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 10), new Duration(TimeUnit.HOUR, 12)),
            new Money("R90.00", RAND));

        // [12 hours .. 1 day] : R100.00
        tariffs.addTariff(new TimePeriod(new Duration(TimeUnit.HOUR, 12), new Duration(TimeUnit.DAY, 1)),
            new Money("R100.00", RAND));

        System.out.println("Car Park Simulator");
        System.out.printf("The current time is %s.\n", clock.examine().toString());
        System.out.println("Commands: tariffs, advance {minutes}, arrive, depart, quit.");
        System.out.print(">");
        String input = keyboard.next().toLowerCase();
        while (!input.equals("quit"))
        {
            if (input.equals("tariffs"))
                System.out.println(tariffs.toString());
            else if (input.equals("advance"))
            {
                // Advance the clock, print the current time.
                clock.advance(new Duration(TimeUnit.MINUTE, keyboard.nextInt()));
                System.out.printf("The current time is %s.\n", clock.examine().toString());
            }
            else if (input.equals("arrive"))
            {
                // Create a new ticket, add it to the register, print details of ticket issued.
                Ticket newTicket = new Ticket(clock.examine());
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

                    Money tarriffCost = tariffs.getTariff(stayDuration);
                    System.out.printf("Cost of stay : %s.\n", tarriffCost.toString());
                }
            }
            else
            {
                System.out.println("That command is not recognised.");
                System.out.println("Commands: tariffs, advance <minutes>, arrive, depart, quit.");
            }

            System.out.print(">");
            input = keyboard.next().toLowerCase();
        }

        keyboard.close();
        System.out.println("Goodbye.");
    }
}
