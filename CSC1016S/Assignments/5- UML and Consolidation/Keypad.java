/* The Keypad class gets input from the user. Synonymous with the ATM keypad.
 * @author: Lebeko Poulo
 * @ Date: 26/08/2024
 */

import java.util.Scanner;

public class Keypad {
    private Scanner input;

    public Keypad() {
        input = new Scanner(System.in);
    }

    public int getInput() {
        return input.nextInt();
    }

    public double getDoubleInput() {
        return input.nextDouble();
    }
}
