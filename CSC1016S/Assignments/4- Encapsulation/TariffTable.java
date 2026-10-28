/**
 * Container class for storing and accessing {@link ParkingTariff} objects.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 14/08/24
 */
public class TariffTable
{
    /**
     * Creates a new {@link TariffTable} with the given maximum number of entries.
     *
     * @param maxSize the maximum capacity to initialize the internal container with.
     */
    public TariffTable(int maxSize)
    {
        this.parkingTariffs = new ParkingTariff[maxSize];
        this.nextFree = 0;
    }

    /**
     * Adds a new tariff to the table for the given {@link TimePeriod}. The specified {@link TimePeriod} must directly
     * follow the {@link TimePeriod} of the previously added tariff otherwise an {@link IllegalArgumentException} is thrown.
     *
     * @param period the {@link TimePeriod} of this tariff.
     * @param tariff the {@link Money} cost of this tariff for the given {@code period}.
     * @throws IllegalArgumentException if {@code period} does not directly follow the previous tariff's time period.
     */
    public void addTariff(TimePeriod period, Money tariff) throws IllegalArgumentException
    {
        if ((this.nextFree > 0) && !this.parkingTariffs[this.nextFree - 1].isDirectlyFollowedBy(period))
            throw new IllegalArgumentException("Tariff periods must be adjacent.");

        this.parkingTariffs[this.nextFree++] = new ParkingTariff(period, tariff);
    }

    /**
     * @return The {@link Money} tariff cost associated with {@code lengthOfStay} in this table.
     */
    public Money getTariff(Duration lengthOfStay)
    {
        final Currency RAND = new Currency("R", "ZAR", 100);

        for (int i = 0; i < this.nextFree; ++i)
        {
            if (this.parkingTariffs[i].containsDuration(lengthOfStay))
                return this.parkingTariffs[i].getCost();
        }

        return new Money(0, RAND);
    }

    /**
     * Returns a string representation of this instance.
     *
     * @return a string in the format
     * <pre>{@code '<timePeriod0> : <cost0>
     * ...
     * <timePeriodn> : <costn>'
     * }</pre>
     */
    public String toString()
    {
        String res = "";
        for (int i = 0; i < this.nextFree; ++i)
        {
            res += this.parkingTariffs[i].toString();
            if (i != (this.nextFree - 1))
                res += '\n';
        }

        return res;
    }

    private ParkingTariff[] parkingTariffs;
    private int nextFree;
}
