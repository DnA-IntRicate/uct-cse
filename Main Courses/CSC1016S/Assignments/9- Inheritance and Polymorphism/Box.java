/**
 * TODO: BOX
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Box extends Component
{
    public Box(String serialNumber, String manufacturer, String color, int memoryMb)
    {
        super(serialNumber, manufacturer, color);
        m_MemoryMb = memoryMb;
    }

    public Box()
    {
        super();
        m_MemoryMb = 0;
    }

    public int GetMemoryMb() { return m_MemoryMb; }
    public void SetMemoryMb(int memoryMb) { m_MemoryMb = memoryMb; }

    @Override
    public String toString()
    {
        return String.format("Box: %s, %s, %s, %d", m_SerialNumber, m_Manufacturer, m_Color, m_MemoryMb);
    }

    private int m_MemoryMb;
}
