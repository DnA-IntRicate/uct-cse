/**
 * Drawing vertical lines in {@link Question3} and {@link VectorGraphics}. Inherits from {@link VectorObject}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see HLine
 * @see PtLine
 * @see Rectangle
 */
public class VLine extends VectorObject
{
    /**
     * Create a new {@link VLine} with the given {@code id}, {@code x}-coord, {@code y}-coord and {@code length}.
     *
     * @param id the ID of the line
     * @param x the x-coordinate of the line
     * @param y the y-coordinate of the line
     * @param length the vertical length of the line
     */
    public VLine(int id, int x, int y, int length)
    {
        super(id, x, y);
        m_Length = length;
    }

    /**
     * Draw this vertical line onto the given {@code matrix}.
     *
     * @param matrix the 2-dimensional character matrix to draw this line onto
     */
    @Override
    public void draw(char[][] matrix)
    {
        // Since this is a row-major matrix [row][col], the x and y coordinates must be swapped.
        for (int i = this.y; i < (this.y + m_Length); ++i)
            matrix[i][this.x] = '*';
    }

    // The vertical length of this line.
    private int m_Length;
}
