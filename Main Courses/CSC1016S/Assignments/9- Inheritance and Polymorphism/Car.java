/**
 * TODO: CAR
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Car extends Vehicle
{
    public Car(int numCylinders, String manufacturer, Student owner, int numSeats, double weight)
    {
        super(numCylinders, manufacturer, owner);

        m_NumSeats = numSeats;
        m_Weight = weight;
    }

    public Car(final Car other)
    {
        super(other);

        m_NumSeats = other.m_NumSeats;
        m_Weight = other.m_Weight;
    }

    @Override
    public String toString()
    {
        return String.format("%s\nThe car is a %d-seater weighing %.1f kg", super.toString(), m_NumSeats, m_Weight);
    }

    private int m_NumSeats;
    private double m_Weight;
}
