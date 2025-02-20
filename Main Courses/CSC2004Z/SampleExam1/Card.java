import java.util.Objects;
import java.util.Scanner;

/**
 * Its a card.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 20/02/25
 */
public class Card
{
    public Card(final String shape, final String color, final String pattern)
    {
        m_Shape = shape;
        m_Color = color;
        m_Pattern = pattern;
    }

    /**
     * Constructs a new {@link Card} from a {@link String} in the format: {@code "shape,color,pattern"}
     * @param cardEntry the string to construct the new {@link Card} from
     */
    public Card(final String cardEntry)
    {
        try (Scanner scanner = new Scanner(cardEntry))
        {
            scanner.useDelimiter(",");

            m_Shape = scanner.next();
            m_Color = scanner.next();
            m_Pattern = scanner.next();
        }
    }

    public String GetShape() { return m_Shape; }
    public String GetColor() { return m_Color; }
    public String GetPattern() { return m_Pattern; }

    @Override
    public boolean equals(Object other)
    {
        if (!(other instanceof Card))
            return false;

        Card myCard = (Card)other;
        return m_Shape.equals(myCard.m_Shape) && m_Color.equals(myCard.m_Color) && m_Pattern.equals(myCard.m_Pattern);
    }

    @Override
    public int hashCode()
    {
        return Objects.hash(m_Shape, m_Color, m_Pattern);
    }

    private String m_Shape;
    private String m_Color;
    private String m_Pattern;
}
