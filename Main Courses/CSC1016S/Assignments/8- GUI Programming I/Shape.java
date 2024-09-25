/**
 * The base class for all shapes.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 25/09/24
 */
public abstract class Shape
{
    /**
     * Create a new {@link Shape} with the given {@code color} and {@code filled} flag.
     *
     * @param color the color of the shape
     * @param filled is the shape filled
     */
    public Shape(String color, boolean filled)
    {
        m_Color = color;
        m_Filled = filled;
    }

    /**
     * Default constructor.
     */
    public Shape()
    {
        m_Color = "";
        m_Filled = false;
    }

    /**
     * Calculates the area of this shape. This method is abstract and is intended to be overriden by all derived classes.
     *
     * @return the area of this shape
     */
    public abstract double getArea();

    /**
     * Calculates the perimeter of this shape. This method is abstract and is intended to be overriden by all derived
     * classes.
     *
     * @return the perimeter of this shape
     */
    public abstract double getPerimeter();

    /**
     * Get the color of this shape.
     *
     * @return the color of this shape
     */
    public String getColor() { return m_Color; }

    /**
     * Set the color of this shape.
     *
     * @param color the new color to set
     */
    public void setColor(String color) { m_Color = color; }

    /**
     * Get the filled flag of this shape.
     *
     * @return the filled flag of this shape
     */
    public boolean isFilled() { return m_Filled; }

    /**
     * Set the filled flag of this shape.
     *
     * @param filled the new filled flag to set
     */
    public void setFilled(boolean filled) { m_Filled = filled; }

    /**
     * Returns a string representation of this shape.
     *
     * @return a string in the format {@code 'Color: <color> Filled: <filled>'}
     */
    @Override
    public String toString()
    {
        return String.format("Color: %s Filled: %b", m_Color, m_Filled);
    }

    /**
     * Checks for equality between this shape and the given shape {@code other}.
     *
     * @param other the shape to compare this shape against
     * @return {@code true} if and only if {@code other} is not null and equals this shape, {@code false} otherwise
     */
    public boolean equals(final Shape other)
    {
        if (other == null)
            return false;

        if (this == other)
            return true;

        return m_Color.equals(other.m_Color) && (m_Filled == other.m_Filled);
    }

    /** The color of this shape. */
    private String m_Color;

    /** The filled flag of this shape. */
    private boolean m_Filled;
}
