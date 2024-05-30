import java.util.Random;
import java.util.Scanner;
import java.text.MessageFormat;


public class RockPaperScissors
{
    public static final String ROCK = "Rock";
    public static final String PAPER = "Paper";
    public static final String SCISSORS = "Scissors";

    private static final String[] CHOICES = {ROCK, PAPER, SCISSORS};

    public static String ComputeChoice()
    {
        Random rnd = new Random();
        int rndIndex = rnd.nextInt(CHOICES.length);

        return CHOICES[rndIndex];
    }

    public static boolean PlayerWon(String player, String computer)
    {
        if (player.equals(ROCK) && computer.equals(SCISSORS))
            return true;

        if (player.equals(PAPER) && computer.equals(ROCK))
            return true;

        if (player.equals(SCISSORS) && computer.equals(PAPER))
            return true;

        return false;
    }

    public static String Input(String prompt, Scanner scanner)
    {
        System.out.print(prompt);

        return scanner.nextLine();
    }

    public static void main(String[] args)
    {
        Scanner scanner = new Scanner(System.in);

        System.out.println(MessageFormat.format("{0}, {1}, {2}!", ROCK, PAPER, SCISSORS));
        System.out.println("=========================================================");

        String userChoice = Input(MessageFormat.format("Enter your choice: {0}, {1} or {2}: ", ROCK, PAPER, SCISSORS), scanner);
        String computerChoice = ComputeChoice();

        System.out.println("=========================================================");
        System.out.println("Your choice: " + userChoice);
        System.out.println("My choice: " + computerChoice);

        if (userChoice.equals(computerChoice))
            System.out.println("It's a tie!");
        else if (PlayerWon(userChoice, computerChoice))
            System.out.println("You won!");
        else
            System.out.println("You lost!");

        scanner.close();
    }
}
