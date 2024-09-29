/**
 * Represents a triangle. Inherits from {@link Shape}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 25/09/24
 */
public class Triangle extends Shape
{
    /**
     * Create a {@link Triangle} with the given side-lengths {@code s1}, {@code s2}, {@code s3}, the color {@code color} and
     * the filled flag {@code filled}.
     *
     * @param s1 side 1 of the triangle
     * @param s2 side 2 of the triangle
     * @param s3 side 3 of the triangle
     * @param color the color of the triangle
     * @param filled is the triangle filled
     */
    public Triangle(double s1, double s2, double s3, String color, boolean filled)
    {
        super(color, filled);
        m_S1 = s1;
        m_S2 = s2;
        m_S3 = s3;
    }

    /**
     * Create a {@link Triangle} with the given side-lengths {@code s1}, {@code s2} and {@code s3}.
     * Default-initializes the {@code color} and {@code filled} fields.
     *
     * @param s1 side 1 of the triangle
     * @param s2 side 2 of the triangle
     * @param s3 side 3 of the triangle
     */
    public Triangle(double s1, double s2, double s3)
    {
        super();
        m_S1 = s1;
        m_S2 = s2;
        m_S3 = s3;
    }

    /**
     * Default constructor.
     */
    public Triangle()
    {
        super();
        m_S1 = 1.0;
        m_S2 = 1.0;
        m_S3 = 1.0;
    }

    /**
     * Get the length of side 1 of this triangle.
     *
     * @return the length of side 1 of this triangle
     */
    public double getSide1() { return m_S1; }

    /**
     * Set the length of side 1 of this triangle.
     *
     * @param s1 the new length of side 1 to set
     */
    public void setSide1(double s1) { m_S1 = s1; }

    /**
     * Get the length of side 2 of this triangle.
     *
     * @return the length of side 2 of this triangle
     */
    public double getSide2() { return m_S2; }

    /**
     * Set the length of side 2 of this triangle.
     *
     * @param s2 the new length of side 2 to set
     */
    public void setSide2(double s2) { m_S2 = s2; }

    /**
     * Get the length of side 3 of this triangle.
     *
     * @return the length of side 3 of this triangle
     */
    public double getSide3() { return m_S3; }

    /**
     * Set the length of side 3 of this triangle.
     *
     * @param s3 the new length of side 3 to set
     */
    public void setSide3(double s3) { m_S3 = s3; }

    /**
     * Calculate the area of this triangle. Implements Heron's formula for the area of a triangle.
     *
     * @return the area of this triangle
     *
     * @see Shape#getArea()
     */
    @Override
    public double getArea()
    {
        double s = (m_S1 + m_S2 + m_S3) * 0.5;
        return Math.sqrt(s * (s - m_S1) * (s - m_S2) * (s - m_S3));
    }

    /**
     * Calculate the perimeter of this triangle.
     *
     * @return the perimeter of this triangle
     *
     * @see Shape#getPerimeter()
     */
    @Override
    public double getPerimeter()
    {
        return m_S1 + m_S2 + m_S3;
    }

    /**
     * Returns a string representation of this shape.
     *
     * @return a string in the format {@code 'Color: <color> Filled: <filled> S1: <s1> S2: <s2> S3: <s3>'}
     */
    @Override
    public String toString()
    {
        return String.format("%s S1: %.2f S2: %.2f S3: %.2f", super.toString(), m_S1, m_S2, m_S3);
    }

    /**
     * Checks for equality between this triangle and the given triangle {@code other}.
     *
     * @param other the triangle to compare this triangle against
     * @return {@code true} if and only if {@code other} is not null and equals this triangle, {@code false} otherwise
     *
     * @see Shape#equals(Shape)
     */
    public boolean equals(final Triangle other)
    {
        if (!((Shape)other).equals(this))
            return false;

        return (m_S1 == other.m_S1) && (m_S2 == other.m_S2) && (m_S3 == other.m_S3);
    }

    /** The length of side 1 of this triangle. */
    private double m_S1;

    /** The length of side 2 of this triangle. */
    private double m_S2;

    /** The length of side 3 of this triangle. */
    private double m_S3;
}
