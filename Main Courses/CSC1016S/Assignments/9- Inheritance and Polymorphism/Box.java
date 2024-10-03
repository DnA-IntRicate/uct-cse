/**
 * A computer box component for use in {@link Question1}. Inherits from {@link Component}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Accessory
 * @see Screen
 */
public class Box extends Component
{
    /**
     * Create a new {@link Box} with the given {@code serialNumber}, {@code manufacturer}, {@code color} and
     * {@code memoryMb}.
     *
     * @param serialNumber the serial number of the box
     * @param manufacturer the manufacturer of the box
     * @param color the color of the box
     * @param memoryMb the amount of memory of the box in megabytes
     */
    public Box(String serialNumber, String manufacturer, String color, int memoryMb)
    {
        super(serialNumber, manufacturer, color);
        m_MemoryMb = memoryMb;
    }

    /**
     * Default constructor.
     */
    public Box()
    {
        super();
        m_MemoryMb = 0;
    }

    /**
     * Get the amount of memory of this box in megabytes.
     *
     * @return the amount of memory in megabytes
     */
    public int GetMemoryMb() { return m_MemoryMb; }

    /**
     * Set the amount of memory of this box.
     *
     * @param memoryMb the new amount of memory in megabytes to set
     */
    public void SetMemoryMb(int memoryMb) { m_MemoryMb = memoryMb; }

    /**
     * @return a string in the format: {@code "Box: <serialNumber>, <manufacturer>, <color>, <memory>"}
     */
    @Override
    public String toString()
    {
        return String.format("Box: %s, %s, %s, %d", m_SerialNumber, m_Manufacturer, m_Color, m_MemoryMb);
    }

    // The amount of memory of this box in megabytes.
    private int m_MemoryMb;
}
