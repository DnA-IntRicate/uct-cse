/**
 * Stores the information of a car for use in {@link Question3}. Inherits from {@link Vehicle}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Student
 */
public class Car extends Vehicle
{
    /**
     * Create a new {@link Car} with the given information.
     *
     * @param numCylinders the number of cylinders of the car
     * @param manufacturer the manufacturer of the car
     * @param owner the {@link Student} owner of the car
     * @param numSeats the number of seats of the car
     * @param weight the weight of the car in kilograms
     */
    public Car(int numCylinders, String manufacturer, Student owner, int numSeats, double weight)
    {
        super(numCylinders, manufacturer, owner);

        m_NumSeats = numSeats;
        m_Weight = weight;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Car} to copy
     */
    public Car(final Car other)
    {
        super(other);

        m_NumSeats = other.m_NumSeats;
        m_Weight = other.m_Weight;
    }

    /**
     * @return a string representation in the format: {@code "<Vehicle.toString>\nThe car is a <numSeats>-seater
     * weighing <weight> kg"}
     *
     * @see Vehicle#toString()
     */
    @Override
    public String toString()
    {
        return String.format("%s\nThe car is a %d-seater weighing %.1f kg", super.toString(), m_NumSeats, m_Weight);
    }

    // The number of seats of this car.
    private int m_NumSeats;

    // The weight of the vehicle in kilograms.
    private double m_Weight;
}
