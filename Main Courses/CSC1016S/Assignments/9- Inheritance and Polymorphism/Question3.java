import java.util.Scanner;

/**
 * TODO: Question 3
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Question3
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

    private static void Cleanup()
    {
        s_Scanner.close();
    }

    // TODO: Code cleanup
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

        Student owner = new Student(ownerName, ownerAge, ownerGender, ownerInstitution, ownerStudyProgram, 0, ownerHobbies);
        Car car = new Car(numCylinders, manufacturer, owner, numSeats, weight);

        Print(car.toString());
        Cleanup();
    }

    private static Scanner s_Scanner;
}
