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
    private static final Color COLOR_MISSING = new Color(1.0f, 0.0f, 1.0f, 1.0f); // Magenta

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

            return COLOR_MISSING;
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

        m_XInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
        m_YInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));

        m_FilledCheckBox = new JCheckBox("Filled", false);

        m_InterfaceLayout = new CardLayout();
        m_InterfacePanel = new JPanel(m_InterfaceLayout);
        //m_InterfacePanel.add(m_ShapesComboBox);

        m_RectangleInterfacePanel = new JPanel(new FlowLayout());
        // m_RectangleInterfacePanel.add(m_ShapesComboBox);
        m_RectangleInterfacePanel.add(m_DrawShapeButton);
        m_RectangleInterfacePanel.add(m_ColorsComboBox);
        m_RectangleInterfacePanel.add(m_RectWidthInput);
        m_RectangleInterfacePanel.add(m_RectHeightInput);
        m_RectangleInterfacePanel.add(m_FilledCheckBox);
        m_RectangleInterfacePanel.add(new JLabel("X:"));
        m_RectangleInterfacePanel.add(m_XInput);
        m_RectangleInterfacePanel.add(new JLabel("Y:"));
        m_RectangleInterfacePanel.add(m_YInput);

        m_CircleInterfacePanel = new JPanel(new FlowLayout());
        m_CircleInterfacePanel.add(new JLabel("NEW LABEL"));

        m_ViewportPanel = new JPanel(null);
        m_ViewportPanel.setDoubleBuffered(true);
        m_ViewportPanel.setBackground(COLOR_MISSING);
        // m_ViewportPanel.paintComponents(getGraphics());

        m_InterfacePanel.setPreferredSize(new Dimension(500, 300)); // Top half
        m_ViewportPanel.setPreferredSize(new Dimension(500, 300));  // Bottom half

        m_InterfacePanel.add(m_CircleInterfacePanel, "CircleInterfacePanel");
        m_InterfacePanel.add(m_RectangleInterfacePanel, "RectangleInterfacePanel");
    }

    public void Initialize()
    {
        setSize(500, 700);
        setLayout(new FlowLayout());
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        add(m_ShapesComboBox);
        // add(new JPanel());
        add(m_InterfacePanel);
        add(m_ViewportPanel);

        setVisible(true);
    }

    // TODO: make these functions private?
    public void Clear(Graphics g, final Color clearCol)
    {
        m_ViewportPanel.paintComponents(g);
        g.setColor(clearCol);
        g.fillRect(0, 0, m_ViewportPanel.getWidth(), m_ViewportPanel.getHeight());
    }

    public void DrawCircle(final Circle circle, int x, int y)
    {
        Log("Drawing Circle: " + circle.toString());

        Graphics2D g = (Graphics2D)m_ViewportPanel.getGraphics();
        Clear(g, COLOR_MISSING);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Utils.StrColorToColor(circle.getColor()));

        int diameter = (int)circle.getRadius() * 2;
        if (circle.isFilled())
            g.fillOval(x, y, diameter, diameter);
        else
            g.drawOval(x, y, diameter, diameter);
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

    public void DrawTriangle(final Triangle tri, int x, int y)
    {
        Log("Drawing Triangle: " + tri.toString());

        Graphics2D g = (Graphics2D)m_ViewportPanel.getGraphics();
        Clear(g, COLOR_MISSING);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(Utils.StrColorToColor(tri.getColor()));

        double sideA = tri.getSide1();
        double sideB = tri.getSide2();
        double sideC = tri.getSide3();

        // Calculate angles using the Law of Cosines
        double angleA = Math.acos(((sideB * sideB) + (sideC * sideC) - (sideA * sideA)) / (2 * sideB * sideC));
        double angleB = Math.acos(((sideA * sideA) + (sideC * sideC) - (sideB * sideB)) / (2 * sideA * sideC));
        double angleC = Math.PI - angleA - angleB; // Triangle sum theorem
        // TODO: Remove this

        // Assuming one vertex is at (x, y) (the starting point)
        int ax = x;
        int ay = y;

        int bx = (int) (ax + sideC * Math.cos(angleB)); // Using angleB at vertex A
        int by = (int) (ay + sideC * Math.sin(angleB));

        int cx = (int) (ax + sideB * Math.cos(angleA)); // Using angleA at vertex A
        int cy = (int) (ay + sideB * Math.sin(angleA));

        // Create arrays for the points
        int[] xPoints = { ax, bx, cx };
        int[] yPoints = { ay, by, cy };

        if (tri.isFilled())
            g.fillPolygon(xPoints, yPoints, 3);
        else
            g.drawPolygon(xPoints, yPoints, 3);
    }

    private void onDrawShape(ActionEvent e)
    {
        switch ((String)m_ShapesComboBox.getSelectedItem())
        {
            case SHAPE_STR_CIRCLE:
                Circle circle = new Circle();
                // Radius, color, filled
                DrawCircle(circle, (int)m_XInput.getValue(), (int)m_YInput.getValue());

                break;

            case SHAPE_STR_RECTANGLE:
                Rectangle rect = new Rectangle();
                rect.setWidth((double)(int)m_RectWidthInput.getValue());
                rect.setHeight((double)(int)m_RectHeightInput.getValue());
                rect.setColor((String)m_ColorsComboBox.getSelectedItem());
                rect.setFilled(m_FilledCheckBox.isSelected());
                DrawRectangle(rect, (int)m_XInput.getValue(), (int)m_YInput.getValue());
                break;

            case SHAPE_STR_TRIANGLE:
                Triangle tri = new Triangle();
                // Side1..3, color, filled
                DrawTriangle(tri, (int)m_XInput.getValue(), (int)m_YInput.getValue());
                break;
        }
    }

    private void onShapeSelected(ActionEvent e)
    {
        String selectedShape = (String)m_ShapesComboBox.getSelectedItem();
        Log("Selected %s.", selectedShape);

        switch (selectedShape)
        {
            case SHAPE_STR_CIRCLE:
                m_InterfaceLayout.show(m_InterfacePanel, "CircleInterfacePanel");
                break;

            case SHAPE_STR_RECTANGLE:
                m_InterfaceLayout.show(m_InterfacePanel, "RectangleInterfacePanel");
                break;

            case SHAPE_STR_TRIANGLE:
                m_InterfaceLayout.show(m_InterfacePanel, "TriangleInterfacePanel");
                break;
        }
    }

    private static void Log(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    public static void main(String[] args)
    {
        ShapeMaker maker = new ShapeMaker();
        maker.Initialize(); // Rename this function to run?
    }

    private JButton m_DrawShapeButton;
    private JComboBox<String> m_ShapesComboBox;
    private JComboBox<String> m_ColorsComboBox;

    private JCheckBox m_FilledCheckBox;

    private JSpinner m_RectWidthInput;
    private JSpinner m_RectHeightInput;
    private JSpinner m_XInput;
    private JSpinner m_YInput;



    private CardLayout m_InterfaceLayout;
    private JPanel m_InterfacePanel;


    private JPanel m_RectangleInterfacePanel;
    private JPanel m_CircleInterfacePanel;
    private JPanel m_TriangleInterfacePanel;

    private JPanel m_ViewportPanel;
    // private Viewport m_Viewport;

    // TODO: Create a label with the text "Dimensions" and under it put all shape dimension stuff
}
