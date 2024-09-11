import java.util.Scanner;
//
public class TestVector {

    // This class does not define a type of object, so we don't want anyone trying to create an instance.
    private TestVector() {}

    private static int getSelection(Scanner scanner) {
        System.out.println("\nMake a selection and press return:");
        System.out.print("(0) Quit, ");
        System.out.print("(1) Test getMagnitude(), ");
        System.out.println("(2) Test add()");
        System.out.print("(3) Test scalar multiply(), ");
        System.out.println("(4) Test dotProduct()");
        return scanner.nextInt();
    }

    private static Vector makeVector(Scanner scanner) {
        System.out.println("Enter x component and y component (separated by a space):");
        return new Vector(scanner.nextInt(), scanner.nextInt());
    }

    public static void main(String[] args) {

        final Scanner scanner = new Scanner(System.in);

        int selection = getSelection(scanner);

        while (selection!=0) {

            if (selection==1) {
                final Vector vOne = TestVector.makeVector(scanner);
                System.out.println("Created a Vector object with the given values for vx and vy.");
                System.out.printf("Result of calling getMagnitude(): %.2f\n", vOne.getMagnitude() );
            }
            else if (selection==2){
                final Vector vOne = TestVector.makeVector(scanner);
                System.out.println("Created Vector object: "+vOne);
                final Vector vTwo = TestVector.makeVector(scanner);
                System.out.println("Created Vector object: "+vTwo);

                final Vector vThree = vOne.add(vTwo);
                System.out.println("Result of adding the vectors: "+vThree);
            }
            else if (selection==3) {
                final Vector vOne = TestVector.makeVector(scanner);
                System.out.println("Created Vector object: "+vOne);
                System.out.println("Enter multiplier:");
                final double multiplier = scanner.nextDouble();
                final Vector vTwo = vOne.multiply(multiplier);
                System.out.println("New Vector: "+vTwo);
            }
            else if (selection==4) {
                final Vector vOne = TestVector.makeVector(scanner);
                System.out.println("Created Vector object: "+vOne);
                final Vector vTwo = TestVector.makeVector(scanner);
                System.out.println("Created Vector object: "+vTwo);

                final double result = vOne.dotProduct(vTwo);
                System.out.println("Result of dot product of the vectors: "+result);
            }
            else {
                System.out.println("That selection was not recognised.");
            }

            selection = getSelection(scanner);
        }

        scanner.close();
    }


}
