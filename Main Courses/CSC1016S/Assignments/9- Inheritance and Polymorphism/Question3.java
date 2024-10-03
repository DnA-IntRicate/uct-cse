import java.util.Scanner;

/**
 * A simple program for inputting vehicle and student info.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Person
 * @see Student
 * @see Vehicle
 * @see Car
 */
public class Question3
{
    public static void main(String[] args)
    {
        String manufacturer = Input("Enter the vehicle manufacturer:");
        String ownerName = Input("Enter the name of the vehicle owner:");
        String ownerGender = Input("Enter the owner's gender:");
        String ownerStudyProgram = Input("Enter the owner's programme of study:");
        String ownerInstitution = Input("Enter the owner's Institution name:");
        String ownerHobbies = Input("Enter the owner's hobbies:");
        int ownerAge = Integer.parseInt(Input("Enter the owner's age:"));
        int numCylinders = Integer.parseInt(Input("Enter the number of cylinders in the engine:"));
        int numSeats = Integer.parseInt(Input("Enter the car seating capacity:"));
        double weight = Double.parseDouble(Input("Enter the weight of the car:"));

        // Set yearOfStudy to 0 since it is not currently being used.
        Student owner = new Student(ownerName, ownerAge, ownerGender, ownerInstitution, ownerStudyProgram, 0, ownerHobbies);
        Car car = new Car(numCylinders, manufacturer, owner, numSeats, weight);

        Print(car.toString());
        Cleanup();
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

    // Cleanup program resources before closing.
    private static void Cleanup()
    {
        s_Scanner.close();
    }

    // This program's scanner.
    private static Scanner s_Scanner;
}
