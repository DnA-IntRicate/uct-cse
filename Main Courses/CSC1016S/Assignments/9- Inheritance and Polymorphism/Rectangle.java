/**
 * Drawing rectangles in {@link Question3} and {@link VectorGraphics}. Inherits from {@link VectorObject}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see HLine
 * @see PtLine
 * @see VLine
 */
public class Rectangle extends VectorObject
{
    /**
     * Create a new {@link Rectangle} with the given {@code id}, {@code x}-coord, {@code y}-coord, {@code width}
     * and {@code height}.
     *
     * @param id the ID of the rectangle
     * @param x the x-coordinate of the rectangle
     * @param y the y-coordinate of the rectangle
     * @param width the width of the rectangle
     * @param height the height of the rectangle
     */
    public Rectangle(int id, int x, int y, int width, int height)
    {
        super(id, x, y);
        m_Width = width;
        m_Height = height;
    }

    /**
     * Draw this rectangle onto the given {@code matrix}.
     *
     * @param matrix the 2-dimensional character matrix to draw this rectangle onto
     */
    @Override
    public void draw(char[][] matrix)
    {
        // Since this is a row-major matrix [row][col], the x and y coordinates must be swapped.
        for (int i = this.y; i < Math.min(matrix.length, this.y + m_Height); ++i)
        {
            for (int j = this.x; j < Math.min(matrix[0].length, this.x + m_Width); ++j)
                matrix[i][j] = '*';
        }
    }

    // The width of this rectangle.
    private int m_Width;

    // The height of this rectangle.
    private int m_Height;
}
