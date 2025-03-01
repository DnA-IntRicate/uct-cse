/**
 * Represents a line in 2-dimensional space for use in {@link Ships}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class Line
{
    public Line(String lineStr)
    {
        String[] numbers = lineStr.split(" ");
        this.a = Double.parseDouble(numbers[0]);
        this.b = Double.parseDouble(numbers[1]);
        this.c = Double.parseDouble(numbers[2]);
        this.x = Double.parseDouble(numbers[3]);
        this.y = Double.parseDouble(numbers[4]);
    }

    public double a;
    public double b;
    public double c;
    public double x;
    public double y;
}
