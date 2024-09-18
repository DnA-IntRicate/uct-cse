/**
 * An implementation of the 'Cows and Bulls' number guessing game.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 18/09/24
 */
public class CowsAndBulls
{
    /** The number of digits of the mystery number. */
    public final static int NUM_DIGITS = 4;

    /** The maximum value of the mystery number. */
    public final static int MAX_VALUE = 9876;

    /** The minimum value of the mystery number. */
    public final static int MIN_VALUE = 1234;

    /** The maximum number of guesses a player has in the game. */
    public final static int MAX_GUESSES = 10;

    /**
     * Create a CowsAndBulls game using the given randomisation {@code seed} value to generate a mystery
     * number of {@link #NUM_DIGITS} length, and that gives the player {@link #MAX_GUESSES} guesses.
     *
     * @param seed the value to generate the mystery number off of
     */
    public CowsAndBulls(int seed)
    {
        NumberPicker picker = new NumberPicker(seed, 1, 9);
        for (int i = 0; (i < NUM_DIGITS) && picker.hasNext(); ++i)
            m_Number = (m_Number * 10) + picker.nextInt();

        // Clamp in-case the number exceeds the valid bounds. Using 'Math.clamp(long, int, int)' did not work with Automark
        m_Number = Math.max(MIN_VALUE, Math.min(m_Number, MAX_VALUE));
        m_GuessesRemaining = MAX_GUESSES;
        m_GuessedCorrectly = false;
    }

    /**
     * Evaluates a guess that the mystery number is {@code guessNumber} and returns the outcome as a
     * {@link Result} object. Decrements the remaining guesses. Assumes that the game is not over.
     *
     * @param guessNumber the number the user has guessed
     * @return a {@link Result} containing the number of cows and bulls of the guess
     */
    public Result guess(int guessNumber)
    {
        int bulls = NumberUtils.countMatches(m_Number, guessNumber);
        int cows = NumberUtils.countIntersect(m_Number, guessNumber) - bulls;
        Result res = new Result(cows, bulls);

        m_GuessesRemaining--;
        m_GuessedCorrectly = m_Number == guessNumber;

        return res;
    }

    /**
     * Ends the game and returns the mystery number.
     *
     * @return the mystery number of the game
     */
    public int giveUp()
    {
        m_GuessesRemaining = 0;
        return m_Number;
    }

    /**
     * Checks if the mystery number has been guessed correctly or if there are no more guesses remaining.
     *
     * @return {@code true} if the game is over, otherwise {@code false}
     */
    public boolean gameOver()
    {
        return m_GuessedCorrectly || (m_GuessesRemaining == 0);
    }

    /**
     * Get the number of guesses remaining.
     *
     * @return the number of guesses remaining
     */
    public int guessesRemaining() { return m_GuessesRemaining; }

    /** The mystery number of this game. */
    private int m_Number;

    /** The number of guesses remaining of this game. */
    private int m_GuessesRemaining;

    /** Stores if the user guessed the mystery number correctly in the current game. */
    private boolean m_GuessedCorrectly;
}
