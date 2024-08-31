/* 
 * @author: Lebeko Poulo
 * @ Date: 26/08/2024
 */

public class ATM {
    private boolean userAuthenticated;
    private int currentAccountNumber;
    private BankDatabase bankDatabase;
    private Screen screen;
    private Keypad keypad;
    private CashDispenser cashDispenser;
    private DepositSlot depositSlot;

    public ATM() {
        userAuthenticated = false;
        bankDatabase = new BankDatabase();
        screen = new Screen();
        keypad = new Keypad();
        cashDispenser = new CashDispenser();
        depositSlot = new DepositSlot();
    }

    public void start() {
        while (!userAuthenticated) {
            screen.displayMessage("Enter account number: ");
            int accountNumber = keypad.getInput();
            screen.displayMessage("Enter PIN: ");
            int pin = keypad.getInput();

            userAuthenticated = bankDatabase.authenticateUser(accountNumber, pin);

            if (userAuthenticated) {
                currentAccountNumber = accountNumber;
                performTransactions();
            } else {
                screen.displayMessage("Invalid account number or PIN. Please try again.");
            }
        }
    }

    private void performTransactions() {
        boolean userExited = false;

        while (!userExited) {
            screen.displayMessage("Main menu:");
            screen.displayMessage("1. View balance");
            screen.displayMessage("2. Withdraw cash");
            screen.displayMessage("3. Deposit funds");
            screen.displayMessage("4. Exit");

            int choice = keypad.getInput();

            switch (choice) {
                case 1:
                    displayBalance();
                    break;
                case 2:
                    performWithdrawal();
                    break;
                case 3:
                    performDeposit();
                    break;
                case 4:
                    userExited = true;
                    break;
                default:
                    screen.displayMessage("Invalid selection. Try again.");
                    break;
            }
        }
    }

    private void displayBalance() {
        double availableBalance = bankDatabase.getAvailableBalance(currentAccountNumber);
        double totalBalance = bankDatabase.getTotalBalance(currentAccountNumber);

        screen.displayMessage("Available Balance: " + availableBalance);
        screen.displayMessage("Total Balance: " + totalBalance);
    }

    private void performWithdrawal() {
        screen.displayMessage("Enter amount to withdraw: ");
        double amount = keypad.getDoubleInput();
        Withdrawal withdrawal = new Withdrawal(currentAccountNumber, amount, bankDatabase, cashDispenser);
        withdrawal.execute();
    }

    private void performDeposit() {
        screen.displayMessage("Enter deposit amount: ");
        double amount = keypad.getDoubleInput();
        screen.displayMessage("Insert deposit envelope.");
        if (depositSlot.isEnvelopeReceived()) {
            bankDatabase.credit(currentAccountNumber, amount);
            screen.displayMessage("Deposit successful.");
        } else {
            screen.displayMessage("Deposit failed. Envelope not received.");
        }
    }
}
