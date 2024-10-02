/**
 * TODO: VLINE
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class VLine extends VectorObject
{
    public VLine(int id, int x, int y, int length)
    {
        super(id, x, y);
        m_Length = length;
    }

    // Treat as a row-major matrix ... [row][col]
    @Override
    public void draw(char[][] matrix)
    {
        /** Math.min(matrix.length, this.y + m_Length) */
        for (int i = this.y; i < (this.y + m_Length); ++i)
            matrix[i][this.x] = '*';
    }

    private int m_Length;
}
