import java.util.Scanner;

/**
 * CSC1016S Practest2E code given to students
 *
 * @version 1.0
 */
public class Test {

    public static void main(String[] args) {
        Scanner s = new Scanner(System.in);
        int option;
        Planet[] planets = new Planet[100];
        int index = 0;
        System.out.println("**** Welcome to the CS planet inventory system ****");

        do {
            System.out.println("Enter choice: ");
            System.out.println("1. Add new planet (not rocky or gas giant).");
            System.out.println("2. Add new rocky planet.");
            System.out.println("3. Add new gas giant.");
            System.out.println("4. Quit");
            option = s.nextInt();
            s.nextLine();
            if (option != 4) {
                System.out.println("Enter planet name:");
                String name = s.nextLine();
                System.out.println("Enter planet mass:");
                double mass = s.nextDouble();
                s.nextLine();
                System.out.println("Enter planet density:");
                double density = s.nextDouble();
                s.nextLine();
                Planet newPlanet = null;
                switch (option) {
                    case 1:
                        newPlanet = new Planet(name, mass, density);
                        break;
                    case 2:
                        System.out.println("Enter number of moons:");
                        newPlanet = new RockyPlanet(name, mass, density, s.nextInt());
                        s.nextLine();
                        break;
                    case 3:
                        System.out.println("Does this planet have rings? ('y' or 'n')");
                        boolean hasRings = s.nextLine().toLowerCase().equals("y");
                        newPlanet = new GasGiant(name, mass, density, hasRings);
                }

                boolean duplicate = false;
                for (int i = 0; i < planets.length; i++) {
                    Planet planet = planets[i];
                    if (planet != null && planet.equals(newPlanet)) {
                        System.out.println("A planet with that name already exists: \n" + planet);
                        duplicate = true;
                    }
                }
                if (!duplicate) {
                    planets[index++] = newPlanet;
                }
            }
        } while (option != 4);
        System.out.println("Showing all planets in the inventory:");
        for (int i = 0; i < planets.length; i++) {
            Planet planet = planets[i];
            if (planet != null) {
                System.out.println(planet);
            }
        }

        s.close();
    }

}
