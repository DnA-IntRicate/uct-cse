/**
 * A screen component for use in {@link Question1}. Inherits from {@link Component}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Accessory
 * @see Box
 */
public class Screen extends Component
{
    /**
     * Create a new {@link Screen} with the given {@code serialNumber}, {@code manufacturer}, {@code color} and the
     * {@code sizeInches} screen size.
     *
     * @param serialNumber the serial number of the screen
     * @param manufacturer the manufacturer of the screen
     * @param color the color of the screen
     * @param sizeInches the size of the screen in inches
     */
    public Screen(String serialNumber, String manufacturer, String color, int sizeInches)
    {
        super(serialNumber, manufacturer, color);
        m_SizeInches = sizeInches;
    }

    /**
     * Default constructor.
     */
    public Screen()
    {
        super();
        m_SizeInches = 0;
    }

    /**
     * Get the size of this screen in inches.
     *
     * @return the size in inches
     */
    public int GetSizeInches() { return m_SizeInches; }

    /**
     * Set the size of this screen.
     *
     * @param sizeInches the new size in inches
     */
    public void SetSizeInches(int sizeInches) { m_SizeInches = sizeInches; }

    /**
     * @return a string in the format: {@code "Screen: <serialNumber>, <color>, <manufacturer>, <size>"}
     */
    @Override
    public String toString()
    {
        return String.format("Screen: %s, %s, %s, %d", m_SerialNumber, m_Color, m_Manufacturer, m_SizeInches);
    }

    // The size of this screen in inches.
    private int m_SizeInches;
}
