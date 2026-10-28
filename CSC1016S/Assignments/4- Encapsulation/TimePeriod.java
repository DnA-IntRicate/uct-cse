/**
 *  Represents a {@link Duration} range specified by a lower and upper {@link Duration}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 14/08/24
 */
public class TimePeriod
{
    /**
     * Creates a new {@link TimePeriod} with the given inclusive lower bound and exclusive upper bound.
     *
     * @param lowerBound the lower bound of this {@link TimePeriod}.
     * @param upperBound the upper bound of this {@link TimePeriod}.
     */
    public TimePeriod(Duration lowerBound, Duration upperBound)
    {
        this.lowerBound = lowerBound;
        this.upperBound = upperBound;
    }

    /**
     * @return The lower bound of this instance.
     */
    public Duration lowerBound()
    {
        return this.lowerBound;
    }

    /**
     * @return The upper bound of this instance.
     */
    public Duration upperBound()
    {
        return this.upperBound;
    }

    /**
     * Checks if the given {@link Duration} is within this instance's upper (inclusive) and lower bounds.
     *
     * @return {@code true} if this instance includes {@code duration}, otherwise {@code false}.
     */
    public boolean includes(Duration duration)
    {
        return (this.lowerBound.compareTo(duration) <= 0) && (this.upperBound.compareTo(duration) > 0);
    }

    /**
     * Checks if this instance comes before the given {@link TimePeriod}.
     *
     * @return {@code true} if this instance precedes {@code other}, otherwise {@code false}.
     */
    public boolean precedes(TimePeriod other)
    {
        return this.upperBound.compareTo(other.lowerBound()) <= 0;
    }

    /**
     * Checks if this instance is adjacent to the given {@link TimePeriod}.
     *
     * @return {@code true} if this instance is adjacent to {@code other}, otherwise {@code false}.
     */
    public boolean adjacent(TimePeriod other)
    {
        return (this.upperBound.compareTo(other.lowerBound()) == 0) || (this.lowerBound.compareTo(other.upperBound()) == 0);
    }

    /**
     * Returns a string representation of this instance.
     *
     * @return a string in the format {@code '[<lowerBound> .. <upperBound>]'}.
     */
    public String toString()
    {
        String lowerStr = Duration.format(this.lowerBound, TimeUnit.MINUTE);
        String upperStr = Duration.format(this.upperBound, TimeUnit.MINUTE);

        return String.format("[%s .. %s]", lowerStr, upperStr);
    }

    private Duration lowerBound;
    private Duration upperBound;
}
