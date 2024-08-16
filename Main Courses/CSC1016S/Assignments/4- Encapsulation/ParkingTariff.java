/**
 * Represents a parking tariff to be used by {@link TariffTable}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 14/08/24
 */
public class ParkingTariff
{
    /**
     * Creates a new {@link ParkingTariff} from a {@link TimePeriod} object and a {@link Money} object.
     *
     * @param timePeriod the time period of this {@link ParkingTariff}.
     * @param cost the cost of this {@link ParkingTariff}.
     */
    public ParkingTariff(TimePeriod timePeriod, Money cost)
    {
        this.timePeriod = timePeriod;
        this.cost = cost;
    }

    /**
     * Default constructor.
     */
    public ParkingTariff()
    {
        this.timePeriod = new TimePeriod(Duration.ZERO, Duration.ZERO);
        this.cost = new Money(0, new Currency("R", "ZAR", 100));
    }

    /**
     * Check if {@code duration} is included in this instance's {@link TimePeriod}.
     *
     * @return {@code true} if {@code duration} is included in this instance's {@link TimePeriod}, otherwise {@code false}.
     */
    public boolean containsDuration(Duration duration)
    {
        return this.timePeriod.includes(duration);
    }

    /**
     * Check if this instance's {@link TimePeriod} precedes and is adjacent to {@code period}.
     *
     * @return {@code true} if {@code period} direcly follows this instance's {@link TimePeriod}, otherwise {@code false}.
     */
    public boolean isDirectlyFollowedBy(TimePeriod period)
    {
        return this.timePeriod.precedes(period) && this.timePeriod.adjacent(period);
    }

    /**
     * @return This instance's {@link TimePeriod}.
     */
    public TimePeriod getTimePeriod()
    {
        return this.timePeriod;
    }

    /**
     * Sets this instance's {@link TimePeriod}.
     *
     * @param period the new value.
     */
    public void setTimePeriod(TimePeriod period)
    {
        this.timePeriod = period;
    }

    /**
     * @return This instance's tariff cost as a {@link Money} object.
     */
    public Money getCost()
    {
        return this.cost;
    }

    /**
     * Set this instance's tariff cost as a {@link Money} object.
     *
     * @param cost the new value.
     */
    public void setMoney(Money cost)
    {
        this.cost = cost;
    }

    /**
     * Returns a string representation of this instance.
     *
     * @return a string in the format {@code '<timePeriod> : <cost>'}.
     */
    public String toString()
    {
        return String.format("%s : %s", this.timePeriod.toString(), this.cost.toString());
    }

    private TimePeriod timePeriod;
    private Money cost;
}
