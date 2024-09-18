/**
 * Represents a circle. Inherits from {@link Shape}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 18/09/24
 */
public class Circle extends Shape
{
    /**
     * Create a new {@link Circle} with the given {@code name}, {@code color} and {@code radius}.
     *
     * @param name the name of the circle
     * @param color the color of the circle
     * @param radius the radius of the circle
     */
    public Circle(String name, String color, double radius)
    {
        super(name, color);
        m_Radius = radius;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Circle} to copy into this instance
     */
    public Circle(final Circle other)
    {
        super(other);
        m_Radius = other.m_Radius;
    }

    /**
     * Returns a string representation of this circle.
     *
     * @return a string in the format {@code '<name> <color> Radius <radius>'}
     */
    @Override
    public String toString()
    {
        return String.format("%s Radius %.1f", super.toString(), m_Radius);
    }

    /** The radius of this circle. */
    private double m_Radius;
}
