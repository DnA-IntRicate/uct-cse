/**
 * TODO: ACCESSORY
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Accessory extends Component
{
    public Accessory(String serialNumber, String manufacturer, String color)
    {
        super(serialNumber, manufacturer, color);
    }

    public Accessory()
    {
        super();
    }

    @Override
    public String toString()
    {
        return String.format("Accessories: %s, %s, %s", m_SerialNumber, m_Manufacturer, m_Color);
    }
}
