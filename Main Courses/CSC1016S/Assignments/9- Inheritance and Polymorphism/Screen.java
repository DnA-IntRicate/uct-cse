/**
 * TODO: SCREEN
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Screen extends Component
{
    public Screen(String serialNumber, String manufacturer, String color, int sizeInches)
    {
        super(serialNumber, manufacturer, color);
        m_SizeInches = sizeInches;
    }

    public Screen()
    {
        super();
        m_SizeInches = 0;
    }

    public int GetSizeInches() { return m_SizeInches; }
    public void SetSizeInches(int memoryMb) { m_SizeInches = memoryMb; }

    @Override
    public String toString()
    {
        return String.format("Screen: %s, %s, %s, %d", m_SerialNumber, m_Color, m_Manufacturer, m_SizeInches);
    }

    private int m_SizeInches;
}
