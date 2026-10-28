/**
 * Represents a rectangle. Inherits from {@link Shape}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 25/09/24
 */
public class Rectangle extends Shape
{
    /**
     * Create a new {@link Rectangle} with the given {@code width}, {@code height}, {@code color} and {@code filled} flag.
     *
     * @param width the width of the rectangle
     * @param height the height of the rectangle
     * @param color the color of the rectangle
     * @param filled is the rectangle filled
     */
    public Rectangle(double width, double height, String color, boolean filled)
    {
        super(color, filled);
        m_Width = width;
        m_Height = height;
    }

    /**
     * Create a new {@link Rectangle} with the given {@code width} and {@code height}.
     * Default-initializes the {@code color} and {@code filled} fields.
     *
     * @param width the width of the rectangle
     * @param height the height of the rectangle
     */
    public Rectangle(double width, double height)
    {
        super();
        m_Width = width;
        m_Height = height;
    }

    /**
     * Default constructor.
     */
    public Rectangle()
    {
        super();
        m_Width = 0.0;
        m_Height = 0.0;
    }

    /**
     * Get the width of this rectangle.
     *
     * @return the width of this rectangle
     */
    public double getWidth() { return m_Width; }

    /**
     * Set the width of this rectangle.
     *
     * @param width the new width to set
     */
    public void setWidth(double width) { m_Width = width; }

    /**
     * Get the height of this rectangle.
     *
     * @return the height of this rectangle
     */
    public double getHeight() { return m_Height; }

    /**
     * Set the height of this rectangle.
     *
     * @param height the new height to set
     */
    public void setHeight(double height) { m_Height = height; }

    /**
     * Calculate the area of this rectangle.
     *
     * @return the area of this rectangle
     *
     * @see Shape#getArea()
     */
    @Override
    public double getArea()
    {
        return m_Width * m_Height;
    }

    /**
     * Calculate the perimeter of this rectangle.
     *
     * @return the perimeter of this rectangle
     *
     * @see Shape#getPerimeter()
     */
    @Override
    public double getPerimeter()
    {
        return (2.0 * m_Width) + (2.0 * m_Height);
    }

    /**
     * Returns a string representation of this shape.
     *
     * @return a string in the format {@code 'Color: <color> Filled: <filled> Width: <width> Height: <height>'}
     */
    @Override
    public String toString()
    {
        return String.format("%s Width: %.2f Height: %.2f", super.toString(), m_Width, m_Height);
    }

    /**
     * Checks for equality between this rectangle and the given rectangle {@code other}.
     *
     * @param other the rectangle to compare this rectangle against
     * @return {@code true} if and only if {@code other} is not null and equals this rectangle, {@code false} otherwise
     *
     * @see Shape#equals(Shape)
     */
    public boolean equals(final Rectangle other)
    {
        if (!((Shape)other).equals(this))
            return false;

        return (m_Width == other.m_Width) && (m_Height == other.m_Height);
    }

    /** The width of this rectangle. */
    private double m_Width;

    /** The height of this rectangle. */
    private double m_Height;
}
