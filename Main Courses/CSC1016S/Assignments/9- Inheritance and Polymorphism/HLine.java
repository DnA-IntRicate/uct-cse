/**
 * TODO: HLINE
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class HLine extends VectorObject
{
    public HLine(int id, int x, int y, int length)
    {
        super(id, x, y);
        m_Length = length;
    }

    // Treat as a row-major matrix ... [row][col]
    @Override
    public void draw(char[][] matrix)
    {
        /** Math.min(matrix[0].length, this.x + m_Length) */
        for (int i = this.x; i < (this.x + m_Length); ++i)
            matrix[this.y][i] = '*';
    }

    private int m_Length;
}
