import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.function.Consumer;

/**
 * TODO: Desc
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 25/09/24
 */
public class ShapeMaker extends JFrame
{
    private static final String COLOR_STR_BLACK = "Black";
    private static final String COLOR_STR_RED = "Red";
    private static final String COLOR_STR_GREEN = "Green";
    private static final String COLOR_STR_BLUE = "Blue";

    private static final String SHAPE_STR_CIRCLE = "Circle";
    private static final String SHAPE_STR_RECTANGLE = "Rectangle";
    private static final String SHAPE_STR_TRIANGLE = "Triangle";

    private static final Color COLOR_CLEAR = new Color(1.0f, 1.0f, 1.0f, 1.0f);
    private static final Color COLOR_MISSING = new Color(1.0f, 0.0f, 1.0f, 1.0f);

    private class Utils
    {
        public static <_Ty> void RegisterComponentCallback(JComboBox<_Ty> component, Consumer<ActionEvent> callback)
        {
            component.addActionListener(new ActionListener()
            {
                @Override
                public void actionPerformed(ActionEvent e) { callback.accept(e); }
            });
        }

        public static void RegisterComponentCallback(JButton component, Consumer<ActionEvent> callback)
        {
            component.addActionListener(new ActionListener()
            {
                @Override
                public void actionPerformed(ActionEvent e) { callback.accept(e); }
            });
        }

        public static Color StrColorToColor(String colorStr)
        {
            switch (colorStr)
            {
                case COLOR_STR_BLACK:   return new Color(0.0f, 0.0f, 0.0f, 1.0f);
                case COLOR_STR_RED:     return new Color(1.0f, 0.0f, 0.0f, 1.0f);
                case COLOR_STR_GREEN:   return new Color(0.0f, 1.0f, 0.0f, 1.0f);
                case COLOR_STR_BLUE:    return new Color(0.0f, 0.0f, 1.0f, 1.0f);
            }

            // Magenta
            return new Color(1.0f, 0.0f, 1.0f, 1.0f);
        }
    }

    public ShapeMaker()
    {
        super("Shape Maker");

        final String[] SHAPES_STRINGS = { SHAPE_STR_CIRCLE, SHAPE_STR_RECTANGLE, SHAPE_STR_TRIANGLE };
        m_ShapesComboBox = new JComboBox<String>(SHAPES_STRINGS);
        Utils.RegisterComponentCallback(m_ShapesComboBox, e -> { onShapeSelected(e); });

        final String[] COLORS_STRINGS = { COLOR_STR_BLACK, COLOR_STR_RED, COLOR_STR_GREEN, COLOR_STR_BLUE };
        m_ColorsComboBox = new JComboBox<String>(COLORS_STRINGS);

        m_DrawShapeButton = new JButton("Draw");
        Utils.RegisterComponentCallback(m_DrawShapeButton, e -> { onDrawShape(e); });

        m_RectWidthInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
        m_RectHeightInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));

        m_FilledCheckBox = new JCheckBox("Filled", false);

        // We like double-buffering
       // m_Viewport = new Viewport(0, 50, 300, 400, true);
       // m_Viewport.SetClearColor(new Color(1.0f, 0.0f, 1.0f, 1.0f));

        m_InterfacePanel = new JPanel(new FlowLayout());
        m_InterfacePanel.add(m_ShapesComboBox);
        m_InterfacePanel.add(m_DrawShapeButton);
        m_InterfacePanel.add(m_ColorsComboBox);
        m_InterfacePanel.add(m_RectWidthInput);
        m_InterfacePanel.add(m_RectHeightInput);
        m_InterfacePanel.add(m_FilledCheckBox);

        m_ViewportPanel = new JPanel(null);
        m_ViewportPanel.setBackground(COLOR_MISSING);
        // m_ViewportPanel.paintComponents(getGraphics());

        m_InterfacePanel.setPreferredSize(new Dimension(800, 300)); // Top half
        m_ViewportPanel.setPreferredSize(new Dimension(800, 300));  // Bottom half
    }

    public void Initialize()
    {
        setSize(800, 600);
        setLayout(new GridLayout());    // FlowLayout
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        add(m_InterfacePanel);
        add(m_ViewportPanel);

        setVisible(true);
    }

    public void Clear(Graphics g, final Color clearCol)
    {
        m_ViewportPanel.paintComponents(g);
        g.setColor(clearCol);
        g.fillRect(0, 0, m_ViewportPanel.getWidth(), m_ViewportPanel.getHeight());
    }

    public void DrawRectangle(final Rectangle rect, int x, int y)
    {
        Log("Drawing Rectangle: " + rect.toString());

        Graphics2D g = (Graphics2D)m_ViewportPanel.getGraphics();
        Clear(g, COLOR_MISSING);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Utils.StrColorToColor(rect.getColor()));

        if (rect.isFilled())
            g.fillRect(x, y, (int)rect.getWidth(), (int)rect.getHeight());
        else
            g.drawRect(x, y, (int)rect.getWidth(), (int)rect.getHeight());
    }

    public void onDrawShape(ActionEvent e)
    {
        switch ((String)m_ShapesComboBox.getSelectedItem())
        {
            case SHAPE_STR_CIRCLE:
                break;

            case SHAPE_STR_RECTANGLE:
                Rectangle rect = new Rectangle();
                rect.setWidth((double)(int)m_RectWidthInput.getValue());
                rect.setHeight((double)(int)m_RectHeightInput.getValue());
                rect.setColor((String)m_ColorsComboBox.getSelectedItem());
                rect.setFilled(m_FilledCheckBox.isSelected());
                DrawRectangle(rect, 0, 0);
                break;

            case SHAPE_STR_TRIANGLE:
                break;

            default:
                break;
        }
    }

    // TODO: Remove
    public void onShapeSelected(ActionEvent e)
    {
        String selectedItem = (String)m_ShapesComboBox.getSelectedItem();
        System.out.println("Selected: " + selectedItem);
    }

    private static void Log(String msg)
    {
        System.out.println(msg);
    }

    public static void main(String[] args)
    {
        ShapeMaker maker = new ShapeMaker();
        maker.Initialize();
    }

    // private JTextField
    private JButton m_DrawShapeButton;
    private JComboBox<String> m_ShapesComboBox;
    private JComboBox<String> m_ColorsComboBox;

    private JCheckBox m_FilledCheckBox;

    private JSpinner m_RectWidthInput;
    private JSpinner m_RectHeightInput;

    private JPanel m_InterfacePanel;
    private JPanel m_ViewportPanel;
    // private Viewport m_Viewport;

    // TODO: Create a label with the text "Dimensions" and under it put all shape dimension stuff
}
