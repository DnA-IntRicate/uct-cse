/**
 * A 2-dimensional vector with {@code x} and {@code y} components.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 11/09/24
 */
public class Vector
{
    /**
     * Creates a new {@link Vector} with the given {@code x} and {@code y} components.
     *
     * @param x the {@code x} component
     * @param y the {@code y} component
     */
    public Vector(double x, double y)
    {
        m_X = x;
        m_Y = y;
    }

    /**
     * Returns the sum of this vector and {@code other}.
     *
     * @param other the vector to add this vector with
     * @return a new vector containing the component-wise sum of this vector and {@code other}
     */
    public Vector add(final Vector other)
    {
        return new Vector(m_X + other.m_X, m_Y + other.m_Y);
    }

    /**
     * Returns the scalar product of this vector and {@code scalar}.
     *
     * @param scalar the value to multiply this vector by
     * @return a new vector containing the scalar product of this vector and {@code scalar}
     */
    public Vector multiply(double scalar)
    {
        return new Vector(m_X * scalar, m_Y * scalar);
    }

    /**
     * Returns the dot product of this vector and {@code other}.
     *
     * @param other the vector to dot this vector with
     * @return the dot product of this vector and {@code other}
     */
    public double dotProduct(final Vector other)
    {
        return (m_X * other.m_X) + (m_Y * other.m_Y);
    }

    /**
     * Returns the magnitude of this vector by computing the root-sum-square of all the components (Pythagoras).
     *
     * @return the magnitude of this vector
     */
    public double getMagnitude()
    {
        return Math.sqrt(Math.pow(m_X, 2.0) + Math.pow(m_Y, 2.0));
    }

    /**
     * Returns a string representation of this vector.
     *
     * @return a string in the format: {@code "v = (<x>, <y>)"}
     */
    public String toString()
    {
        return String.format("v = (%.2f, %.2f)", m_X, m_Y);
    }

    /** The x-component of this vector. */
    private double m_X;

    /** The y-component of this vector. */
    private double m_Y;
}
