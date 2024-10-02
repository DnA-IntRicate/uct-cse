/**
 * Base class for computer components.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public abstract class Component
{
    // This is protected because we want this constructor to be hidden
    protected Component(String serialNumber, String manufacturer, String color)
    {
        m_SerialNumber = serialNumber;
        m_Manufacturer = manufacturer;
        m_Color = color;
    }

    protected Component()
    {
        m_SerialNumber = "";
        m_Manufacturer = "";
        m_Color = "";
    }

    public String GetSerialNumber() { return m_SerialNumber; }
    public void SetSerialNumber(String number) { m_SerialNumber = number; }

    public String GetManufacturer() { return m_Manufacturer; }
    public void SetManufacturer(String manufacturer) { m_Manufacturer = manufacturer; }

    public String GetColor() { return m_Color; }
    public void SetColor(String color) { m_Color = color; }

    public abstract String toString();

    protected String m_SerialNumber;
    protected String m_Manufacturer;
    protected String m_Color;
}
