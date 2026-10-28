/**
 * Represents the cash dispensing system of the {@link ATM} class.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/09/24
 */
public class CashDispenser
{
    /**
     * Default constructor initializes this instance with 30 available notes of denomination 100 (3000 total cash).
     */
    public CashDispenser()
    {
        m_Denomination = 100;
        m_AvailNotes = 30;
    }

    /**
     * Checks if the cash stored in this instance is greater than or equal to {@code amount}.
     *
     * @param amount the amount to check for
     * @return {@code true} if the stored cash is greater than or equal to {@code amount}, otherwise {@code false}
     */
    public boolean isSufficientCashAvailable(double amount)
    {
        return (double)(m_Denomination * m_AvailNotes) >= amount;
    }

    /**
     * Dispenses cash from this instance decreasing the amount of available notes stored.
     *
     * @param amount the amount to dispense
     */
    public void dispenseCash(double amount)
    {
        m_AvailNotes -= (int)amount / m_Denomination;
    }

    /** The denomination of the notes stored in this cash dispenser */
    private int m_Denomination;

    /** The number of notes stored in this cash dispenser */
    private int m_AvailNotes;
}
