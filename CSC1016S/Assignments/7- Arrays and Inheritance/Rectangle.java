/**
 * Represents a rectangle. Inherits from {@link Shape}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 18/09/24
 */
public class Rectangle extends Shape
{
    /**
     * Create a new rectangle with the given {@code name}, {@code color}, {@code length} and {@code width}.
     *
     * @param name the name of the rectangle
     * @param color the color of the rectangle
     * @param length the legnth of the rectangle
     * @param width the width of the rectangle
     */
    public Rectangle(String name, String color, double length, double width)
    {
        super(name, color);
        m_Length = length;
        m_Width = width;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Rectangle} to copy into this instance
     */
    public Rectangle(final Rectangle other)
    {
        super(other);
        m_Length = other.m_Length;
        m_Width = other.m_Width;
    }

    /**
     * Returns a string representation of this rectangle.
     *
     * @return a string in the format {@code '<name> <color> Length <length> Width <width>'}
     */
    @Override
    public String toString()
    {
        return String.format("%s Length %.1f Width %.1f", super.toString(), m_Length, m_Width);
    }

    /** The length of this rectangle. */
    private double m_Length;

    /** The width of this rectangle. */
    private double m_Width;
}
