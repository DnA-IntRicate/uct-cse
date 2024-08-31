/*
 * @author: Lebeko Poulo
 * @ Date: 26/08/2024
 */

public class Withdrawal {
    private int accountNumber;
    private double amount;
    private BankDatabase bankDatabase;
    private CashDispenser cashDispenser;

    public Withdrawal(int accountNumber, double amount, BankDatabase bankDatabase, CashDispenser cashDispenser) {
        this.accountNumber = accountNumber;
        this.amount = amount;
        this.bankDatabase = bankDatabase;
        this.cashDispenser = cashDispenser;
    }

    public void execute() {
        if (bankDatabase.getAvailableBalance(accountNumber) >= amount) {
            if (cashDispenser.isSufficientCashAvailable(amount)) {
                bankDatabase.debit(accountNumber, amount);
                cashDispenser.dispenseCash(amount);
                System.out.println("Withdrawal successful. Please take your cash.");
            } else {
                System.out.println("Insufficient cash in dispenser.");
            }
        } else {
            System.out.println("Insufficient funds in account.");
        }
    }
}
