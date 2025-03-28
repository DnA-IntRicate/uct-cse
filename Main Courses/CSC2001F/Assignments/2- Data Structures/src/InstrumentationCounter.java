/**
 * A centrally-managed system for counting the number of comparison operations performed
 * during searching and insertion in {@link AVLTree}.
 *
 * @see AVLTree
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 23/03/25
 */
public class InstrumentationCounter
{
    /**
     * Delete the default constructor.
     * If only Java allowed the declaration of static classes like C#...
     */
    private InstrumentationCounter() { }

    /**
     * Is instrumentation enabled?
     * This is determined by whether the command-line argument "1" was passed to the program during startup or not.
     *
     * @return {@code true} if instrumentation is enabled, {@code false} otherwise
     */
    public static boolean IsEnabled() { return s_Enabled; }

    /**
     * Sets whether instrumentation should be enabled or not.
     *
     * @param enabled {@code true} if instrumentation should be enabled, {@code false} if not
     */
    public static void SetEnabled(boolean enabled) { s_Enabled = enabled; }

    /**
     * Increments the insert counter.
     */
    public static void IncrementInserts()
    {
        if (!s_Enabled)
            return;

        s_InsertCount++;
    }

    /**
     * Increments the search counter.
     */
    public static void IncrementSearches()
    {
        if (!s_Enabled)
            return;

        s_SearchCount++;
    }

    /**
     * Returns the current insert-comparison count.
     *
     * @return the insert-comparison count
     */
    public static int GetInsertCompCount()
    {
        if (!s_Enabled)
            return -1;

        return s_InsertCount;
    }

    /**
     * Returns the current search-comparison count.
     *
     * @return the search-comparison count
     */
    public static int GetSearchCompCount()
    {
        if (!s_Enabled)
            return -1;

        return s_SearchCount;
    }

    // Is this class enabled?
    private static boolean s_Enabled = false;

    // The insert-comparison count
    private static int s_InsertCount = 0;

    // The search-comparison count
    private static int s_SearchCount = 0;
}
