import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.function.Consumer;

/**
 * TODO: Desc
 * TODO: Do we need to apply a scaling factor?
 *
 * We keepin' it DRY in here
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

    private static final Color COLOR_VIEWPORT = new Color(0.9f, 0.85f, 0.9f, 1.0f);
    private static final Color COLOR_MISSING = new Color(1.0f, 0.0f, 1.0f, 1.0f); // Magenta

    private static final int FRAME_WIDTH = 450;
    private static final int FRAME_HEIGHT = 700;

    private static final int PANEL_INTERFACE_WIDTH = FRAME_WIDTH;
    private static final int PANEL_INTERFACE_HEIGHT = 130;

    private static final int PANEL_VIEWPORT_WIDTH = FRAME_WIDTH;
    private static final int PANEL_VIEWPORT_HEIGHT = FRAME_HEIGHT - PANEL_INTERFACE_HEIGHT;

    /**
     * TODO: Comment, Since this is private it probably doesn't need javadoc comments
     */
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

        public static void SetComponentWidth(JComponent component, int width)
        {
            component.setPreferredSize(new Dimension(width, component.getPreferredSize().height));
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

        public static boolean IsValidTriangle(final Triangle tri)
        {
            double a = tri.getSide1(), b = tri.getSide2(), c = tri.getSide3();
            return ((a + b) > c) && ((a + c) > b) && ((b + c) > a);
        }
    }

    public ShapeMaker()
    {
        super("Shape Maker");

        final String[] SHAPES_STRINGS = { SHAPE_STR_CIRCLE, SHAPE_STR_RECTANGLE, SHAPE_STR_TRIANGLE };
        m_ShapesComboBox = new JComboBox<String>(SHAPES_STRINGS);
        Utils.SetComponentWidth(m_ShapesComboBox, 350);
        Utils.RegisterComponentCallback(m_ShapesComboBox, e -> { onShapeSelected(e); });

        m_DrawShapeButton = new JButton("Draw");
        Utils.RegisterComponentCallback(m_DrawShapeButton, e -> { onDrawShape(e); });
        Utils.SetComponentWidth(m_DrawShapeButton, 400);

        m_InterfaceLayout = new CardLayout();
        m_InterfacePanel = new JPanel(m_InterfaceLayout);

        m_CircleControls = new CircleInterfaceControls();
        m_RectangleControls = new RectangleInterfaceControls();
        m_TriangleControls = new TriangleInterfaceControls();

        m_ViewportPanel = new JPanel(null);
        m_ViewportPanel.setDoubleBuffered(true);
        m_ViewportPanel.setBackground(COLOR_VIEWPORT);

        m_InterfacePanel.setPreferredSize(new Dimension(PANEL_INTERFACE_WIDTH, PANEL_INTERFACE_HEIGHT)); // Top half
        m_ViewportPanel.setPreferredSize(new Dimension(PANEL_VIEWPORT_WIDTH, PANEL_VIEWPORT_HEIGHT));  // Bottom half

        // TODO: Change these string names
        m_InterfacePanel.add(m_CircleControls.Panel, "CircleInterfacePanel");
        m_InterfacePanel.add(m_RectangleControls.Panel, "RectangleInterfacePanel");
        m_InterfacePanel.add(m_TriangleControls.Panel, "TriangleInterfacePanel");
    }

    public void Run()
    {
        setSize(FRAME_WIDTH, FRAME_HEIGHT);
        setResizable(false);
        setLayout(new FlowLayout());
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        add(new JLabel("Shape:"));
        add(m_ShapesComboBox);
        add(m_InterfacePanel);
        add(m_DrawShapeButton);
        add(m_ViewportPanel);

        setVisible(true);
    }

    public void DrawCircle(final Circle circle, int x, int y)
    {
        Log("Drawing Circle: " + circle.toString());

        Graphics2D g = PrepareViewportGraphicsContextForDraw();
        g.setColor(Utils.StrColorToColor(circle.getColor()));

        int diameter = (int)circle.getRadius() * 2;
        if (circle.isFilled())
            g.fillOval(x, y, diameter, diameter);
        else
            g.drawOval(x, y, diameter, diameter);

        // TODO: Use this
        g.drawString("fishy fish fish, fish fish", x + diameter, y + diameter);
    }

    public void DrawRectangle(final Rectangle rect, int x, int y)
    {
        Log("Drawing Rectangle: " + rect.toString());

        Graphics2D g = PrepareViewportGraphicsContextForDraw();
        g.setColor(Utils.StrColorToColor(rect.getColor()));

        if (rect.isFilled())
            g.fillRect(x, y, (int)rect.getWidth(), (int)rect.getHeight());
        else
            g.drawRect(x, y, (int)rect.getWidth(), (int)rect.getHeight());
    }

    public void DrawTriangle(final Triangle tri, int x, int y)
    {
        Log("Drawing Triangle: " + tri.toString());

        Graphics2D g = PrepareViewportGraphicsContextForDraw();
        g.setColor(Utils.StrColorToColor(tri.getColor()));

        int a = (int)tri.getSide1();
        int b = (int)tri.getSide2();
        int c = (int)tri.getSide3();

        int x1 = 0, y1 = 0;           // First vertex at (0, 0)
        int x2 = a, y2 = 0;           // Second vertex at (a, 0)

        double cosTheta = ((a * a) + (b * b) - (c * c)) / (2.0 * a * b);
        double theta = Math.acos(cosTheta);  // Angle in radians

        // Coordinates of the third vertex
        int x3 = (int)(b * Math.cos(theta));
        int y3 = -(int)(b * Math.sin(theta));

        // Draw the triangle
        int[] xPoints = { x1 + x, x2 + x, x3 + x };
        int[] yPoints = { y1 + y, y2 + y, y3 + y };

        if (tri.isFilled())
            g.fillPolygon(xPoints, yPoints, 3);
        else
            g.drawPolygon(xPoints, yPoints, 3);
    }

    // This must be called before every draw
    private Graphics2D PrepareViewportGraphicsContextForDraw()
    {
        Graphics2D res = (Graphics2D)m_ViewportPanel.getGraphics();
        res.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        res.setColor(COLOR_VIEWPORT);
        res.fillRect(0, 0, m_ViewportPanel.getWidth(), m_ViewportPanel.getHeight());

        return res;
    }

    private void onDrawShape(ActionEvent e)
    {
        switch ((String)m_ShapesComboBox.getSelectedItem())
        {
            case SHAPE_STR_CIRCLE:
                Circle circle = new Circle();
                circle.setRadius((double)(int)m_CircleControls.RadiusInput.getValue());
                circle.setColor(m_CircleControls.GetColor());
                circle.setFilled(m_CircleControls.GetFilled());
                DrawCircle(circle, m_CircleControls.GetX(), m_CircleControls.GetY());
                break;

            case SHAPE_STR_RECTANGLE:
                Rectangle rect = new Rectangle();
                rect.setWidth((double)(int)m_RectangleControls.WidthInput.getValue());
                rect.setHeight((double)(int)m_RectangleControls.HeightInput.getValue());
                rect.setColor(m_RectangleControls.GetColor());
                rect.setFilled(m_RectangleControls.GetFilled());
                DrawRectangle(rect, m_RectangleControls.GetX(), m_RectangleControls.GetY());
                break;

            case SHAPE_STR_TRIANGLE:
                Triangle tri = new Triangle();
                tri.setSide1((double)(int)m_TriangleControls.S1Input.getValue());
                tri.setSide2((double)(int)m_TriangleControls.S2Input.getValue());
                tri.setSide3((double)(int)m_TriangleControls.S3Input.getValue());
                tri.setColor(m_TriangleControls.GetColor());
                tri.setFilled(m_TriangleControls.GetFilled());

                if (!Utils.IsValidTriangle(tri))
                {
                    JOptionPane.showMessageDialog(this, "The triangle sides you inputted are invalid.",
                        "Invalid Triangle!", JOptionPane.ERROR_MESSAGE);
                    return;
                }

                DrawTriangle(tri, m_TriangleControls.GetX(), m_TriangleControls.GetY());
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

    private CardLayout m_InterfaceLayout;
    private JPanel m_InterfacePanel;
    private JPanel m_ViewportPanel;

    private JComboBox<String> m_ShapesComboBox;
    private JButton m_DrawShapeButton;

    /** Marked as abstract since this class should never be instantiated directly. */
    private abstract class ShapeInterfaceControls
    {
        public JPanel Panel;
        public JSpinner XInput;
        public JSpinner YInput;
        public JCheckBox FilledCheckBox;
        public JComboBox<String> ColorsComboBox;

        public ShapeInterfaceControls()
        {
            Panel = new JPanel(new GridBagLayout());
            m_Gbc = new GridBagConstraints();
            m_Gbc.insets = new Insets(5, 5, 5, 5);
            m_Gbc.gridx = 0;
            m_Gbc.gridy = 0;
            m_Gbc.anchor = GridBagConstraints.LINE_START;

            XInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            YInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            FilledCheckBox = new JCheckBox("", false); // Using a left-justified label later.

            final String[] COLORS_STRINGS = { COLOR_STR_BLACK, COLOR_STR_RED, COLOR_STR_GREEN, COLOR_STR_BLUE };
            ColorsComboBox = new JComboBox<String>(COLORS_STRINGS);

            Panel.add(new JLabel("X:"), m_Gbc);
            SameLine();
            Panel.add(XInput, m_Gbc);
            SameLine();
            Panel.add(new JLabel("Y:"), m_Gbc);
            SameLine();
            Panel.add(YInput, m_Gbc);
            NewLine();
            Panel.add(new JLabel("Filled:"), m_Gbc);
            SameLine();
            Panel.add(FilledCheckBox, m_Gbc);
            SameLine();
            Panel.add(new JLabel("Color:"), m_Gbc);
            SameLine();
            SpanAvailWidth();
            Panel.add(ColorsComboBox, m_Gbc);

            // This puts all controls rendered by derived classes below the ones rendered here.
            NewLine();
        }

        public int GetX() { return (int)XInput.getValue(); }
        public int GetY() { return (int)YInput.getValue(); }
        public boolean GetFilled() { return FilledCheckBox.isSelected(); }
        public String GetColor() { return (String)ColorsComboBox.getSelectedItem(); }

        protected void SameLine()
        {
            m_Gbc.gridx += 1;
            m_Gbc.anchor = GridBagConstraints.LINE_START;
        }

        protected void NewLine()
        {
            m_Gbc.gridx = 0;
            m_Gbc.gridy += 1;
            m_Gbc.anchor = GridBagConstraints.LINE_START;
        }

        protected void SpanAvailWidth()
        {
            m_Gbc.gridwidth = 4 - m_Gbc.gridx;
            m_Gbc.fill = GridBagConstraints.HORIZONTAL;
        }

        // To ensure everything stays at the top, add a dummy component with weight
        protected void AlignTop()
        {
            m_Gbc.gridx = 0;
            m_Gbc.gridy++;
            m_Gbc.gridwidth = 4;
            m_Gbc.weighty = 1.0;
            m_Gbc.fill = GridBagConstraints.BOTH;
            Panel.add(new JLabel(), m_Gbc);  // Dummy component
        }

        protected GridBagConstraints m_Gbc;
    }

    private class CircleInterfaceControls extends ShapeInterfaceControls
    {
        // TODO: Maybe don't use JSpinner here?
        public JSpinner RadiusInput;

        public CircleInterfaceControls()
        {
            super();

            RadiusInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            Panel.add(new JLabel("Radius:"), m_Gbc);
            SameLine();
            SpanAvailWidth();
            Panel.add(RadiusInput, m_Gbc);
            AlignTop();
        }
    } private CircleInterfaceControls m_CircleControls;

    private class RectangleInterfaceControls extends ShapeInterfaceControls
    {
        public JSpinner WidthInput;
        public JSpinner HeightInput;

        public RectangleInterfaceControls()
        {
            super();

            WidthInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            HeightInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));

            Panel.add(new JLabel("Width:"), m_Gbc);
            SameLine();
            Panel.add(WidthInput, m_Gbc);
            SameLine();
            Panel.add(new JLabel("Height:"), m_Gbc);
            SameLine();
            Panel.add(HeightInput, m_Gbc);
            AlignTop();
        }
    } private RectangleInterfaceControls m_RectangleControls;

    private class TriangleInterfaceControls extends ShapeInterfaceControls
    {
        public JSpinner S1Input;
        public JSpinner S2Input;
        public JSpinner S3Input;

        public TriangleInterfaceControls()
        {
            super();

            S1Input = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            S2Input = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            S3Input = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));

            Panel.add(new JLabel("S1:"), m_Gbc);
            SameLine();
            Panel.add(S1Input, m_Gbc);
            SameLine();
            Panel.add(new JLabel("S2:"), m_Gbc);
            SameLine();
            Panel.add(S2Input, m_Gbc);
            NewLine();
            Panel.add(new JLabel("S3:"), m_Gbc);
            SameLine();
            SpanAvailWidth();
            Panel.add(S3Input, m_Gbc);
            AlignTop();
        }
    } private TriangleInterfaceControls m_TriangleControls;

    public static void main(String[] args)
    {
        ShapeMaker maker = new ShapeMaker();
        maker.Run();
    }
}
