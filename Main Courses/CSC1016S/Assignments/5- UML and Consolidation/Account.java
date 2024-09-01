/**
 * Represents an account stored in a {@link BankDatabase} object in the {@link ATM} class.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 31/08/24
 */
public class Account
{
    /**
     * Creates a new Account from a given account number, pin, available balance and total balance.
     *
     * @param accountNumber the number of the new account
     * @param pin the pin of the new account
     * @param availBalance the available balance of the new account
     * @param totalBalance the total balance of the new account
     */
    public Account(int accountNumber, int pin, double availBalance, double totalBalance)
    {
        m_AccountNumber = accountNumber;
        m_Pin = pin;
        m_AvailBalance = availBalance;
        m_TotalBalance = totalBalance;
    }

    /**
     * Debits this account by subtracting {@code amount} from the available and total balance.
     *
     * @param amount the amount to debit this account by
     */
    public void debit(double amount)
    {
        m_AvailBalance -= amount;
        m_TotalBalance -= amount;
    }

    /**
     * Credits this account by increasing the available and total balance by {@code amount}.
     *
     * @param amount the amount to credit this account by
     */
    public void credit(double amount)
    {
        m_AvailBalance += amount;
        m_TotalBalance += amount;
    }

    /** Checks if the given {@code pin} equals this account's pin.
     *
     * @return {@code true} if {@code pin} equals this account's pin, otherwise {@code false}
     */
    public boolean validatePin(int pin) { return m_Pin == pin; }

    /**
     * Retrieves this account's number.
     *
     * @return the account number
     */
    public int getAccountNumber() { return m_AccountNumber; }

    /**
     * Retrieves this account's available balance.
     *
     * @return the available balance
     */
    public double getAvailableBalance() { return m_AvailBalance; }

    /**
     * Retrieves this account's total balance.
     *
     * @return the total balance
     */
    public double getTotalBalance() { return m_TotalBalance; }

    /** The account number of this account */
    private int m_AccountNumber;

    /** The personal identification number of this account */
    private int m_Pin;

    /** The available balance of this account */
    private double m_AvailBalance;

    /** The total balance of this account. This is the available balance plus the not-yet available balance for this account */
    private double m_TotalBalance;
}
