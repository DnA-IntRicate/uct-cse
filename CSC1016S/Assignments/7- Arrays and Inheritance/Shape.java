/**
 * The base class for all shapes.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 18/09/24
 */
public class Shape
{
    /**
     * Create a new {@link Shape} with the given {@code name} and {@code color}.
     *
     * @param name the name of the shape
     * @param color the color of the shape
     */
    public Shape(String name, String color)
    {
        m_Name = name;
        m_Color = color;
    }

    /**
     * Copy constructor.
     *
     * @param other the {@link Shape} to copy into this instance
     */
    public Shape(final Shape other)
    {
        m_Name = other.m_Name;
        m_Color = other.m_Color;
    }

    /**
     * Returns a string representation of this shape.
     *
     * @return a string in the format {@code '<name> <color>'}
     */
    public String toString()
    {
        return String.format("%s %s", m_Name, m_Color);
    }

    /** The name of this shape. */
    private String m_Name;

    /** The color of this shape. */
    private String m_Color;
}
