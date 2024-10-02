/**
 * TODO: RECTANGLE
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Rectangle extends VectorObject
{
    public Rectangle(int id, int x, int y, int width, int height)
    {
        super(id, x, y);
        m_Width = width;
        m_Height = height;
    }

    @Override
    public void draw(char[][] matrix)
    {
        for (int i = this.x; i < Math.min(matrix.length, this.x + m_Width); ++i)
        {
            for (int j = this.y; j < Math.min(matrix[0].length, this.y + m_Height); ++j)
                matrix[i][j] = '*';
        }
    }

    private int m_Width;
    private int m_Height;
}
