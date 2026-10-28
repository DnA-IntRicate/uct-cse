/**
 * An accessory component for use in {@link Question1}. Inherits from {@link Component}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Box
 * @see Screen
 */
public class Accessory extends Component
{
    /**
     * Create a new {@link Accessory} with the given {@code serialNumber}, {@code manufacturer} and {@code color}.
     *
     * @param serialNumber the serial number of the accessory
     * @param manufacturer the manufacturer of the accessory
     * @param color the color of the accessory
     */
    public Accessory(String serialNumber, String manufacturer, String color)
    {
        super(serialNumber, manufacturer, color);
    }

    /**
     * Default constructor.
     */
    public Accessory()
    {
        super();
    }

    /**
     * @return a string in the format: {@code "Accessories: <serialNumber>, <manufacturer>, <color>"}
     */
    @Override
    public String toString()
    {
        return String.format("Accessories: %s, %s, %s", m_SerialNumber, m_Manufacturer, m_Color);
    }
}
