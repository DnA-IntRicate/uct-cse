/**
 * TODO: PtLine
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class PtLine extends VectorObject
{
    public PtLine(int id, int x, int y, int x2, int y2)
    {
        super(id, x, y);
        m_X2 = x2;
        m_Y2 = y2;
    }

//    @Override
//    public void draw(char[][] matrix)
//    {
//        int x0 = this.x, x1 = m_X2;
//        int y0 = this.y, y1 = m_Y2;
//
//        int dx = Math.abs(x1 - x0);
//        int dy = -Math.abs(y1 - y0);
//        int sx = (x0 < x1) ? 1 : -1;
//        int sy = (y0 < y1) ? 1 : -1;
//        int err = dx + dy;
//
//        while (true)
//        {
//            if ((y0 >= 0) && (y0 < matrix.length) && (x0 >= 0) && (x0 < matrix[0].length))
//                matrix[y0][x0] = '*';
//
//            if ((x0 == x1) && (y0 == y1))
//                break;
//
//            int e2 = 2 * err;
//            if (e2 >= dy)
//            {
//                err += dy;
//                x0 += sx;
//            }
//
//            if (e2 <= dx)
//            {
//                err += dx;
//                y0 += sy;
//            }
//        }
//    }

    // TODO: FIX THIS
    @Override
    public void draw(char[][] matrix)
    {
        boolean steep = Math.abs(m_Y2 - this.y) > Math.abs(m_X2 - this.x);
        if (steep)
        {
            int tmp = this.x;
            this.x = this.y;
            this.y = tmp;

            tmp = m_X2;
            m_X2 = m_Y2;
            m_Y2 = tmp;
        }

        if (this.x > m_X2)
        {
            int tmp = this.x;
            this.x = m_X2;
            m_X2 = tmp;

            tmp = this.y;
            this.y = m_Y2;
            m_Y2 = tmp;
        }

        int ys = (this.y < m_Y2) ? 1 : -1;
        double m = Math.abs(m_Y2 - this.y) / (m_X2 - this.x);
        int myY = this.y;
        double err = 0;

        /** Math.min(matrix.length, m_X2) */
        for (int i = this.x; i <= Math.min(matrix.length, m_X2); ++i)
        {
            if (steep)
                matrix[i][myY] = '*';   // i, myY
            else
                matrix[myY][i] = '*';   // myY, i

            err += m;
            if (err > 0.5)
            {
                myY += ys;
                err -= 1;
            }
        }
    }

    private int m_X2;
    private int m_Y2;
}
