/**
 * Represents a circle. Inherits from {@link Shape}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 25/09/24
 */
public class Circle extends Shape
{
    /**
     * Create a new {@link Circle} with the given {@code radius}, {@code color} and {@code filled} flag.
     *
     * @param radius the radius of the circle
     * @param color the color of the rectangle
     * @param filled is the rectangle filled
     */
    public Circle(double radius, String color, boolean filled)
    {
        super(color, filled);
        m_Radius = radius;
    }

    /**
     * Create a new {@link Circle} with the given {@code radius}.
     * Default-initializes the {@code color} and {@code filled} fields.
     *
     * @param radius the radius of the rectangle
     */
    public Circle(double radius)
    {
        super();
        m_Radius = radius;
    }

    /**
     * Default constructor.
     */
    public Circle()
    {
        super();
        m_Radius = 0.0;
    }

    /**
     * Get the radius of this circle.
     *
     * @return the radius of this circle
     */
    public double getRadius() { return m_Radius; }

    /**
     * Set the radius of this circle.
     *
     * @param radius the new radius to set
     */
    public void setRadius(double radius) { m_Radius = radius; }

    /**
     * Calculate the area of this circle.
     *
     * @return the area of this circle
     *
     * @see Shape#getArea()
     */
    @Override
    public double getArea()
    {
        return Math.PI * Math.pow(m_Radius, 2.0);
    }

    /**
     * Calculate the perimeter (circumference) of this circle.
     *
     * @return the perimeter (circumference) of this circle
     *
     * @see Shape#getPerimeter()
     */
    @Override
    public double getPerimeter()
    {
        return Math.PI * 2.0 * m_Radius;
    }

    /**
     * Returns a string representation of this shape.
     *
     * @return a string in the format {@code 'Color: <color> Filled: <filled> Radius: <radius>'}
     */
    @Override
    public String toString()
    {
        return String.format("%s Radius: %.2f", super.toString(), m_Radius);
    }

    /**
     * Checks for equality between this circle and the given circle {@code other}.
     *
     * @param other the circle to compare this circle against
     * @return {@code true} if and only if {@code other} is not null and equals this circle, {@code false} otherwise
     *
     * @see Shape#equals(Shape)
     */
    public boolean equals(final Circle other)
    {
        if (!((Shape)other).equals(this))
            return false;

        return m_Radius == other.m_Radius;
    }

    /** The radius of the circle. */
    private double m_Radius;
}
