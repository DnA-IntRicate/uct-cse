import java.util.ArrayList;

/**
 * Container class for storing and interacting with {@link Account} objects in the ATM system.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 31/08/24
 */
public class BankDatabase
{
    /**
     * Default constructor initializes this instance with 1 {@link Account} using the constructor call:
     * <pre>{@code new Account(123456, 1234, 1000.0, 1200.00)}</pre>
     */
    public BankDatabase()
    {
        m_Accounts = new ArrayList<Account>();
        m_Accounts.add(new Account(123456, 1234, 1000.0, 1200.00));
    }

    /**
     * Checks if the specified {@code accountNumber} exists and if its {@code pin} is correct.
     *
     * @param accountNumber the account number to check
     * @param pin the pin associated with this {@code accountNumber}
     * @return {@code true} if the account number exists and matches the given pin, otherwise {@code false}
     */
    public boolean authenticateUser(final int accountNumber, final int pin)
    {
        for (final Account account : m_Accounts)
        {
            if (account.getAccountNumber() == accountNumber)
                return account.validatePin(pin);
        }

        return false;
    }

    /**
     * Debits the account associated with {@code accountNumber} if it exists by the given {@code amount}.
     *
     * @param accountNumber the number of the account to debit
     * @param amount the amount to debit the account by
     */
    public void debit(final int accountNumber, final double amount)
    {
        for (Account account : m_Accounts)
        {
            if (account.getAccountNumber() == accountNumber)
            {
                account.debit(amount);
                return; // Exit method immediately
            }
        }
    }

    /**
     * Credits the account associated with {@code accountNumber} if it exists by the given {@code amount}.
     *
     * @param accountNumber the number of the account to credit
     * @param amount the amount to credit the account by
     */
    public void credit(final int accountNumber, final double amount)
    {
        for (Account account : m_Accounts)
        {
            if (account.getAccountNumber() == accountNumber)
            {
                account.credit(amount);
                return; // Exit method immediately
            }
        }
    }

    /**
     * Retrieve the available balance of a specific account.
     *
     * @param accountNumber the number of the account to retrieve the available balance of
     * @return the available balance of the account, or {@code 0.0} if the account doesn't exist
     */
    public double getAvailableBalance(final int accountNumber)
    {
        for (final Account account : m_Accounts)
        {
            if (account.getAccountNumber() == accountNumber)
                return account.getAvailableBalance();
        }

        return 0.0;
    }

    /**
     * Retrieve the total balance of a specific account.
     *
     * @param accountNumber the number of the account to retrieve the total balance of
     * @return the total balance of the account, or {@code 0.0} if the account doesn't exist
     */
    public double getTotalBalance(final int accountNumber)
    {
        for (final Account account : m_Accounts)
        {
            if (account.getAccountNumber() == accountNumber)
                return account.getTotalBalance();
        }

        return 0.0;
    }

    /** Although this functionality is not currently required, an {@link ArrayList} is used to support more than one user of the bank. */
    private ArrayList<Account> m_Accounts;
}
