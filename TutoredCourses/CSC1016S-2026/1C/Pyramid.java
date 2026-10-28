import java.util.Scanner;


public class Pyramid
{
    public static void main(String[] args)
    {
        try (Scanner in = new Scanner(System.in))
        {
            System.out.println("Enter the height of the pyramid:");
            double height = in.nextDouble();

            System.out.println("Enter the length of the square base:");
            double length = in.nextDouble();

            System.out.println("Enter the number of decimal places:");
            int prec = in.nextInt();

            if ((length < 0) || (height < 0))
            {
                System.out.println("Height and base length must be positive.");
                return;
            }

            if (prec < 0)
            {
                System.out.println("The number of decimal places must be non-negative.");
                return;
            }

            double volume = Math.pow(length, 2) * (height / 3);
            double surfaceArea = Math.pow(length, 2) + (2 * length * Math.sqrt((Math.pow(length, 2) / 4) + Math.pow(height, 2)));

            System.out.printf("The volume is %." + prec + "f.\n", volume);
            System.out.printf("The surface area is %." + prec + "f.\n", surfaceArea);
        }
    }
}
