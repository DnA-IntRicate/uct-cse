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
        int x0 = this.x, x1 = m_X1;
        int y0 = this.y, y1 = m_Y1;

        boolean steep = Math.abs(y1 - y0) > Math.abs(x1 - x0);
        if (steep)
        {
            int tmp = x0;
            x0 = y0;
            y0 = tmp;

            tmp = x1;
            x1 = y1;
            y1 = tmp;
        }

        if (x0 > x1)
        {
            int tmp = x0;
            x0 = x1;
            x1 = tmp;

            tmp = y0;
            y0 = y1;
            y1 = tmp;
        }

        int ys = (y0 <y1) ? 1 : -1;
        double m = (double)Math.abs(y1 - y0) / (double)(x1 - x0);
        int y = y0;
        double error = 0.0;

        for (int x = x0; x <= x1; ++x)
        {
            if (steep)
                matrix[x][y] = '*';
            else
                matrix[y][x] = '*';

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
