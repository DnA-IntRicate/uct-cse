/**
 * Base class for computer components for use in {@link Question1}.
 * This class is marked {@code abstract} since it is not intended to be instantiated directly.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 *
 * @see Accessory
 * @see Box
 * @see Screen
 */
public abstract class Component
{
    // Protected constructor to initialize m_SerialNumber, m_Manufacturer and m_Color.
    protected Component(String serialNumber, String manufacturer, String color)
    {
        m_SerialNumber = serialNumber;
        m_Manufacturer = manufacturer;
        m_Color = color;
    }

    // Protected default constructor.
    protected Component()
    {
        m_SerialNumber = "";
        m_Manufacturer = "";
        m_Color = "";
    }

    /**
     * Get this component's serial number.
     *
     * @return the serial number
     */
    public String GetSerialNumber() { return m_SerialNumber; }

    /**
     * Set this component's serial number.
     *
     * @param number the new serial number to set
     */
    public void SetSerialNumber(String number) { m_SerialNumber = number; }

    /**
     * Get this component's manufacturer.
     *
     * @return the manufacturer
     */
    public String GetManufacturer() { return m_Manufacturer; }

    /**
     * Set this manufacturer's serial number.
     *
     * @param manufacturer the new manufacturer to set
     */
    public void SetManufacturer(String manufacturer) { m_Manufacturer = manufacturer; }

    /**
     * Get this component's color
     *
     * @return the color
     */
    public String GetColor() { return m_Color; }

    /**
     * Set this component's color
     *
     * @param color the new color to set
     */
    public void SetColor(String color) { m_Color = color; }

    /**
     * Returns a string representation of this component.
     *
     * @return a string representation of this component
     */
    public abstract String toString();

    // The serial number.
    protected String m_SerialNumber;

    // The manufacturer.
    protected String m_Manufacturer;

    // The color.
    protected String m_Color;
}
