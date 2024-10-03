/**
 * Drawing point-lines in {@link Question3} and {@link VectorGraphics}. Inherits from {@link VectorObject}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see HLine
 * @see Rectangle
 * @see VLine
 */
public class PtLine extends VectorObject
{
    /**
     * Create a new {@link PtLine} with the given parameters.
     *
     * @param id the ID of the line
     * @param x the start x-coordinate of the line
     * @param y the start y-coordinate of the line
     * @param x1 the end x-coordinate of the line
     * @param y1 the end y-coordinate of the line
     */
    public PtLine(int id, int x, int y, int x1, int y1)
    {
        super(id, x, y);
        m_X1 = x1;
        m_Y1 = y1;
    }

    /**
     * Draw this point-line onto the given {@code matrix} using Bresenham's Line Drawing Algorithm.
     *
     * @param matrix the 2-dimensional character matrix to draw this point-line onto
     */
    @Override
    public void draw(char[][] matrix)
    {
        boolean steep = Math.abs(m_Y1 - this.y) > Math.abs(m_X1 - this.x);
        if (steep)
        {
            int tmp = this.x;
            this.x = this.y;
            this.y = tmp;

            tmp = m_X1;
            m_X1 = m_Y1;
            m_Y1 = tmp;
        }

        if (this.x > m_X1)
        {
            int tmp = this.x;
            this.x = m_X1;
            m_X1 = tmp;

            tmp = this.y;
            this.y = m_Y1;
            m_Y1 = tmp;
        }

        int ys = (this.y < m_Y1) ? 1 : -1;
        double m = (double)Math.abs(m_Y1 - this.y) / (double)(m_X1 - this.x);
        int y = this.y;
        double error = 0;

        for (int i = this.x; i <= m_X1; ++i)
        {
            if (steep)
                matrix[i][y] = '*';
            else
                matrix[y][i] = '*';

            error += m;
            if (error > 0.5)
            {
                y += ys;
                error -= 1;
            }
        }
    }

    // The end x-coordinate of this line.
    private int m_X1;

    // The end y-coordinate of this line.
    private int m_Y1;
}
