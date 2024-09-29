import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.function.Consumer;

/**
 * A basic application featuring a graphical user interface allowing the user to draw different shapes on the screen.
 * This program makes use of the {@link Shape}, {@link Circle}, {@link Rectangle} and {@link Triangle} types.
 *
 * The app features an interface allowing the user to select different shapes and specify all relevant information
 * about the shapes before drawing them. The app then draws these shapes and displays their areas and perimeters.
 *
 * <p><i>We keepin' it <b>DRY</b> in here.</i></p>
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 29/09/24
 *
 * @apiNote This program was intentionally written using naming-conventions that don't follow standard Java practices.
 * The developer probably doesn't like Java that much.
 * @apiNote The public API uses {@code PascalCase} for all class names, functions and public fields.
 * All private and or protected fields are prefixed with {@code m_}.
 *
 * @implNote ShapeMaker currently uses 3 different {@link JSpinner} inputs to get the scale of the shapes from the user.
 * The creation of these 3 spinners was copied between the 3 different 'InterfaceControls' classes. Although this
 * particular control is required for all 3 shapes, contrary to the other controls shared between all 3 shapes, this one was
 * not created inside of the 'InterfaceControls' base class to simplify layout handling of this component. Instead, each
 * of the 3 derived classes handles the scale spinner individually. However, this is something that should be reworked in
 * future versions to remove code duplication.
 */
public class ShapeMaker extends JFrame
{
    /** The name of this frame. */
    private static final String FRAME_NAME = "Shape Maker ~ Adam Foflonker (FFLADA001)";

    /** The width of this frame. */
    private static final int FRAME_WIDTH = 450;

    /** The height of this frame. */
    private static final int FRAME_HEIGHT = 700;

    /** The width of the interface panel. */
    private static final int PANEL_INTERFACE_WIDTH = FRAME_WIDTH;

    /** The height of the interface panel. */
    private static final int PANEL_INTERFACE_HEIGHT = 130;

    /** The width of the viewport panel. */
    private static final int PANEL_VIEWPORT_WIDTH = FRAME_WIDTH;

    /** The height of the viewport panel. */
    private static final int PANEL_VIEWPORT_HEIGHT = FRAME_HEIGHT - PANEL_INTERFACE_HEIGHT;

    /** The ID of the circle interface panel. */
    private static final String PANEL_CIRCLE_ID = "CircleInterfacePanel";

    /** The ID of the rectangle interface panel. */
    private static final String PANEL_RECTANGLE_ID = "RectangleInterfacePanel";

    /** The ID of the triangle interface panel. */
    private static final String PANEL_TRIANGLE_ID = "TriangleInterfacePanel";

    /** The offset applied when rendering shape details in the viewport relative to the shape. */
    private static final int SHAPE_TEXT_OFFSET = 5;

    /** Black string. */
    private static final String COLOR_STR_BLACK = "Black";

    /** Red string. */
    private static final String COLOR_STR_RED = "Red";

    /** Green string. */
    private static final String COLOR_STR_GREEN = "Green";

    /** Blue string. */
    private static final String COLOR_STR_BLUE = "Blue";

    /** The color of the viewport: Light Gray. */
    private static final Color COLOR_VIEWPORT = new Color(0.9f, 0.85f, 0.9f, 1.0f);

    /** The missing color: Magenta. */
    private static final Color COLOR_MISSING = new Color(1.0f, 0.0f, 1.0f, 1.0f);

    /** Black. */
    private static final Color COLOR_BLACK = new Color(0.0f, 0.0f, 0.0f, 1.0f);

    /** Red. */
    private static final Color COLOR_RED = new Color(1.0f, 0.0f, 0.0f, 1.0f);

    /** Green. */
    private static final Color COLOR_GREEN = new Color(0.0f, 1.0f, 0.0f, 1.0f);

    /** Blue. */
    private static final Color COLOR_BLUE = new Color(0.0f, 0.0f, 1.0f, 1.0f);

    /** Circle string. */
    private static final String SHAPE_STR_CIRCLE = "Circle";

    /** Rectangle string. */
    private static final String SHAPE_STR_RECTANGLE = "Rectangle";

    /** Triangle string. */
    private static final String SHAPE_STR_TRIANGLE = "Triangle";

    /** Collection of utility functions. */
    private class Utils
    {
        /** Register a callback for when an action is performed by the user on a JComboBox. */
        public static <_Ty> void RegisterComponentCallback(JComboBox<_Ty> component, Consumer<ActionEvent> callback)
        {
            component.addActionListener(new ActionListener()
            {
                @Override
                public void actionPerformed(ActionEvent e) { callback.accept(e); }
            });
        }

        /** Register a callback for when an action is performed by the user on a JButton. */
        public static void RegisterComponentCallback(JButton component, Consumer<ActionEvent> callback)
        {
            component.addActionListener(new ActionListener()
            {
                @Override
                public void actionPerformed(ActionEvent e) { callback.accept(e); }
            });
        }

        /** Set the width of a JComponent. */
        public static void SetComponentWidth(JComponent component, int width)
        {
            component.setPreferredSize(new Dimension(width, component.getPreferredSize().height));
        }

        /** Convert a color-string to a Color. */
        public static Color StrColorToColor(String colorStr)
        {
            switch (colorStr)
            {
                case COLOR_STR_BLACK:   return COLOR_BLACK;
                case COLOR_STR_RED:     return COLOR_RED;
                case COLOR_STR_GREEN:   return COLOR_GREEN;
                case COLOR_STR_BLUE:    return COLOR_BLUE;
            }

            return COLOR_MISSING;
        }

        /** Checks if the given triangle is valid using the Triangle Inequality Theorem. */
        public static boolean IsValidTriangle(final Triangle tri)
        {
            double a = tri.getSide1(), b = tri.getSide2(), c = tri.getSide3();
            return ((a + b) > c) && ((a + c) > b) && ((b + c) > a);
        }
    }

    /** Initialize the application. */
    public ShapeMaker()
    {
        super(FRAME_NAME);
        Log("Initializing JFrame: %s.", FRAME_NAME);

        final String[] SHAPES_STRINGS = { SHAPE_STR_CIRCLE, SHAPE_STR_RECTANGLE, SHAPE_STR_TRIANGLE };
        m_ShapesComboBox = new JComboBox<String>(SHAPES_STRINGS);
        m_ShapesComboBox.setToolTipText("Choose a shape");
        Utils.SetComponentWidth(m_ShapesComboBox, FRAME_WIDTH - 100);
        Utils.RegisterComponentCallback(m_ShapesComboBox, e -> { OnShapeSelected(e); });

        m_DrawShapeButton = new JButton("Draw");
        m_DrawShapeButton.setToolTipText("Draw the shape");
        Utils.RegisterComponentCallback(m_DrawShapeButton, e -> { OnDrawShape(e); });
        Utils.SetComponentWidth(m_DrawShapeButton, FRAME_WIDTH - 150);

        m_ClearViewportButton = new JButton("Clear");
        m_ClearViewportButton.setToolTipText("Clear all drawn shapes");
        Utils.RegisterComponentCallback(m_ClearViewportButton, e -> { OnClearViewport(e); });
        Utils.SetComponentWidth(m_ClearViewportButton, FRAME_WIDTH - 350);

        m_InterfaceLayout = new CardLayout();
        m_InterfacePanel = new JPanel(m_InterfaceLayout);

        m_CircleControls = new CircleInterfaceControls();
        m_RectangleControls = new RectangleInterfaceControls();
        m_TriangleControls = new TriangleInterfaceControls();

        m_ViewportPanel = new JPanel(null);
        m_ViewportPanel.setDoubleBuffered(true); // Perform off-screen rendering first before displaying on screen.
        m_ViewportPanel.setBackground(COLOR_VIEWPORT);

        // Split this frame into a top and bottom half with the interface panel on top and the viewport at the bottom.
        m_InterfacePanel.setPreferredSize(new Dimension(PANEL_INTERFACE_WIDTH, PANEL_INTERFACE_HEIGHT));
        m_ViewportPanel.setPreferredSize(new Dimension(PANEL_VIEWPORT_WIDTH, PANEL_VIEWPORT_HEIGHT));

        m_InterfacePanel.add(m_CircleControls.Panel, PANEL_CIRCLE_ID);
        m_InterfacePanel.add(m_RectangleControls.Panel, PANEL_RECTANGLE_ID);
        m_InterfacePanel.add(m_TriangleControls.Panel, PANEL_TRIANGLE_ID);
    }

    /** Run the application. */
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
        add(m_ClearViewportButton);
        add(m_ViewportPanel);
        setVisible(true);
    }

    /**
     * Clear the viewport.
     */
    public void ClearViewport()
    {
        Log("Clearing Viewport.");

        Graphics2D g = (Graphics2D)m_ViewportPanel.getGraphics();
        g.setColor(COLOR_VIEWPORT);
        g.fillRect(0, 0, m_ViewportPanel.getWidth(), m_ViewportPanel.getHeight());
    }

    /**
     * Draw the given {@code circle} onto the viewport at the given {@code x} and {@code y} coordinates.
     * This {@link Circle} is anchored at its top-left corner and its area and perimeter are displayed at its
     * bottom-right corner.
     *
     * @param circle the {@link Circle} to draw
     * @param x the x-coordinate to draw at
     * @param y the y-coordinate to draw at
     */
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

        int textX = x + diameter + SHAPE_TEXT_OFFSET;
        int textY = y + diameter + SHAPE_TEXT_OFFSET;
        DrawShapeText(circle, g, textX, textY);
    }

    /**
     * Draw the given {@code rect} onto the viewport at the given {@code x} and {@code y} coordinates.
     * This {@link Rectangle} is anchored at its top-left corner and its area and perimeter are displayed at its
     * bottom-right corner.
     *
     * @param rect the {@link Rectangle} to draw
     * @param x the x-coordinate to draw at
     * @param y the y-coordinate to draw at
     */
    public void DrawRectangle(final Rectangle rect, int x, int y)
    {
        Log("Drawing Rectangle: " + rect.toString());

        Graphics2D g = PrepareViewportGraphicsContextForDraw();
        g.setColor(Utils.StrColorToColor(rect.getColor()));

        int width = (int)rect.getWidth(), height = (int)rect.getHeight();
        if (rect.isFilled())
            g.fillRect(x, y, width, height);
        else
            g.drawRect(x, y, width, height);

        int textX = x + width + SHAPE_TEXT_OFFSET;
        int textY = y + height + SHAPE_TEXT_OFFSET;
        DrawShapeText(rect, g, textX, textY);
    }

    /**
     * Draw the given {@code tri} onto the viewport at the given {@code x} and {@code y} coordinates. This {@link Triangle}
     * is anchored at its bottom-left corner and its area and perimeter are displayed at its top-right corner.
     *
     * @param tri the {@link Triangle} to draw
     * @param x the x-coordinate to draw at
     * @param y the y-coordinate to draw at
     */
    public void DrawTriangle(final Triangle tri, int x, int y)
    {
        Log("Drawing Triangle: " + tri.toString());

        Graphics2D g = PrepareViewportGraphicsContextForDraw();
        g.setColor(Utils.StrColorToColor(tri.getColor()));

        int a = (int)tri.getSide1(), b = (int)tri.getSide2(), c = (int)tri.getSide3();

        // Vertex 1 at (0, 0) in local-space.
        int x1 = 0, y1 = 0;

        // Vertex 2 at (a, 0) in local-space.
        int x2 = a, y2 = 0;

        // Cosine law.
        double cosTheta = ((a * a) + (b * b) - (c * c)) / (2.0 * a * b);
        double thetaRadians = Math.acos(cosTheta);

        // Vertex 3 in local-space.
        int x3 = (int)(b * Math.cos(thetaRadians));
        int y3 = -(int)(b * Math.sin(thetaRadians)); // Invert y-coord since down is positive in Swing's coord system.

        // Apply x and y offsets and transform the local-space vertices to world-space.
        int[] xPoints = { x1 + x, x2 + x, x3 + x };
        int[] yPoints = { y1 + y, y2 + y, y3 + y };

        if (tri.isFilled())
            g.fillPolygon(xPoints, yPoints, 3);
        else
            g.drawPolygon(xPoints, yPoints, 3);

        int textX = x + x3 + (2 * SHAPE_TEXT_OFFSET);
        int textY = y + y3 - (2 * SHAPE_TEXT_OFFSET);
        DrawShapeText(tri, g, textX, textY);
    }

    /** Renders the area and perimeter of the given shape as text at the given x and y coordinates. */
    private void DrawShapeText(final Shape s, Graphics2D g, int x, int y)
    {
        g.setColor(COLOR_BLACK);
        g.drawString(String.format("Area: %.2f", s.getArea()), x, y);
        y += g.getFontMetrics().getHeight();
        g.drawString(String.format("Perimeter: %.2f", s.getPerimeter()), x, y);
    }

    /**
     * Since it cannot be guaranteed that the graphics context will persist between different frames and different
     * calls to getGraphics(), this function must be called before every draw to ensure that the proper state and
     * context is set before drawing. This function enables anti-aliasing for smoothing-out the jagged edges of
     * all geometry rendered.
     */
    private Graphics2D PrepareViewportGraphicsContextForDraw()
    {
        Graphics2D res = (Graphics2D)m_ViewportPanel.getGraphics();
        res.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        return res;
    }

    /** Callback event triggered whenever the user selects a shape from the 'shapes' combo box. */
    private void OnShapeSelected(ActionEvent e)
    {
        String selectedShape = (String)m_ShapesComboBox.getSelectedItem();
        Log("Selected %s.", selectedShape);

        // Choose which Shape interface to show.
        switch (selectedShape)
        {
            case SHAPE_STR_CIRCLE:
                m_InterfaceLayout.show(m_InterfacePanel, PANEL_CIRCLE_ID);
                break;

            case SHAPE_STR_RECTANGLE:
                m_InterfaceLayout.show(m_InterfacePanel, PANEL_RECTANGLE_ID);
                break;

            case SHAPE_STR_TRIANGLE:
                m_InterfaceLayout.show(m_InterfacePanel, PANEL_TRIANGLE_ID);
                break;
        }
    }

    /** Callback event triggered whenever the user clicks the 'draw shape' button. */
    private void OnDrawShape(ActionEvent e)
    {
        // Choose which Shape to draw.
        switch ((String)m_ShapesComboBox.getSelectedItem())
        {
            case SHAPE_STR_CIRCLE:
                Circle circle = new Circle();
                circle.setRadius((double)m_CircleControls.GetRadius() * (double)m_CircleControls.GetScale());
                circle.setColor(m_CircleControls.GetColor());
                circle.setFilled(m_CircleControls.GetFilled());
                DrawCircle(circle, m_CircleControls.GetX(), m_CircleControls.GetY());
                break;

            case SHAPE_STR_RECTANGLE:
                Rectangle rect = new Rectangle();
                rect.setWidth((double)m_RectangleControls.GetWidth() * (double)m_RectangleControls.GetScale());
                rect.setHeight((double)m_RectangleControls.GetHeight() * (double)m_RectangleControls.GetScale());
                rect.setColor(m_RectangleControls.GetColor());
                rect.setFilled(m_RectangleControls.GetFilled());
                DrawRectangle(rect, m_RectangleControls.GetX(), m_RectangleControls.GetY());
                break;

            case SHAPE_STR_TRIANGLE:
                Triangle tri = new Triangle();
                tri.setSide1((double)m_TriangleControls.GetS1() * (double)m_TriangleControls.GetScale());
                tri.setSide2((double)m_TriangleControls.GetS2() * (double)m_TriangleControls.GetScale());
                tri.setSide3((double)m_TriangleControls.GetS3() * (double)m_TriangleControls.GetScale());
                tri.setColor(m_TriangleControls.GetColor());
                tri.setFilled(m_TriangleControls.GetFilled());

                // Display a message to the user if the inputted triangle violates the Inequality Theorem.
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

    /** Callback event triggered whenever the user clicks the 'clear' button. */
    private void OnClearViewport(ActionEvent e)
    {
        ClearViewport();
    }

    /** Log messages to System.out. */
    private static void Log(String fmt, Object... args)
    {
        System.out.println(String.format(fmt, args));
    }

    /** The layout of the interface panel. */
    private CardLayout m_InterfaceLayout;

    /** The interface panel. This panel contains all the visual components and widgets interactable by the user. */
    private JPanel m_InterfacePanel;

    /** The viewport panel. This panel is where all the shapes will be drawn onto. */
    private JPanel m_ViewportPanel;

    /** The 'shapes' combo box. This combo box is used to select which shape to draw. */
    private JComboBox<String> m_ShapesComboBox;

    /** The 'draw shape' button. This button draws a shape with the given input-parameters when pressed. */
    private JButton m_DrawShapeButton;

    /** The 'clear viewport' button. This button clears the viewport when pressed. */
    private JButton m_ClearViewportButton;

    /**
     * The base class for all 'InterfaceControls' classes. These classes encapsulate all the widgets and
     * components associated with each different type of shape and initializes their styles and layouts. They also
     * provide a way for external code to interact with these components and retrieve user-inputted values.
     * Marked as abstract since this class is not intended to be instantiated directly.
     */
    private abstract class ShapeInterfaceControls
    {
        /** The interface panel. */
        public JPanel Panel;

        /** The input for the x-coordinate. */
        public JSpinner XInput;

        /** The input for the y-coordinate. */
        public JSpinner YInput;

        /** The input for the filled flag. */
        public JCheckBox FilledCheckBox;

        /** The combo box for selecting the shape's color. */
        public JComboBox<String> ColorsComboBox;

        /** Create components and establish their layouts and styles. */
        public ShapeInterfaceControls()
        {
            Panel = new JPanel(new GridBagLayout());
            m_Gbc = new GridBagConstraints();
            m_Gbc.insets = new Insets(5, 5, 5, 5);
            m_Gbc.gridx = 0;
            m_Gbc.gridy = 0;
            m_Gbc.anchor = GridBagConstraints.LINE_START;

            XInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            XInput.setToolTipText("The X-coordinate to draw the shape at");

            YInput = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));
            YInput.setToolTipText("The Y-coordinate to draw the shape at");

            FilledCheckBox = new JCheckBox("", false); // Using a left-justified label later.
            FilledCheckBox.setToolTipText("Is this shape filled?");

            final String[] COLORS_STRINGS = { COLOR_STR_BLACK, COLOR_STR_RED, COLOR_STR_GREEN, COLOR_STR_BLUE };
            ColorsComboBox = new JComboBox<String>(COLORS_STRINGS);
            ColorsComboBox.setToolTipText("Choose the shape's color");

            Add(new JLabel("X:"));
            SameLine();
            Add(XInput);
            SameLine();
            Add(new JLabel("Y:"));
            SameLine();
            Add(YInput);
            NewLine();
            Add(new JLabel("Filled:"));
            SameLine();
            Add(FilledCheckBox);
            SameLine();
            Add(new JLabel("Color:"));
            SameLine();
            SpanAvailWidth();
            Add(ColorsComboBox);

            // This puts all components rendered by derived classes below the ones rendered here.
            NewLine();
        }

        /** Get the inputted x-coordinate. */
        public int GetX() { return (int)XInput.getValue(); }

        /** Get the inputted y-coordinate. */
        public int GetY() { return (int)YInput.getValue(); }

        /** Get the inputted filled flag. */
        public boolean GetFilled() { return FilledCheckBox.isSelected(); }

        /** Get the selected color. */
        public String GetColor() { return (String)ColorsComboBox.getSelectedItem(); }

        /** Add a component to this panel with the current GridBagConstraints. */
        protected void Add(JComponent component)
        {
            Panel.add(component, m_Gbc);
        }

        /** Render the next component on the same line. */
        protected void SameLine()
        {
            m_Gbc.gridx += 1;
            m_Gbc.anchor = GridBagConstraints.LINE_START;
        }

        /** Render the next component on the next line. */
        protected void NewLine()
        {
            m_Gbc.gridx = 0;
            m_Gbc.gridy += 1;
            m_Gbc.anchor = GridBagConstraints.LINE_START;
        }

        /** Force the next component to span the available width of the container. */
        protected void SpanAvailWidth()
        {
            m_Gbc.gridwidth = 4 - m_Gbc.gridx;
            m_Gbc.fill = GridBagConstraints.HORIZONTAL;
        }

        /** Push all components rendered above this function-call to the top of the container. */
        protected void AlignTop()
        {
            m_Gbc.gridx = 0;
            m_Gbc.gridy++;
            m_Gbc.gridwidth = 4;
            m_Gbc.weighty = 1.0;
            m_Gbc.fill = GridBagConstraints.BOTH;
            Add(new JLabel()); // Dummy component.
        }

        /** The GridBagLayout constraints for use in component-placement. */
        protected GridBagConstraints m_Gbc;
    }

    /** The interface controls for Circles. */
    private class CircleInterfaceControls extends ShapeInterfaceControls
    {
        /** The input for the radius. */
        public JSpinner RadiusInput;

        /** The input for the scale. */
        public JSpinner ScaleInput;

        /** Create components and establish their layouts and styles. */
        public CircleInterfaceControls()
        {
            super();

            RadiusInput = new JSpinner(new SpinnerNumberModel(1, 1, 2 * PANEL_VIEWPORT_WIDTH, 1));
            RadiusInput.setToolTipText("The radius of the circle");

            ScaleInput = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_WIDTH * PANEL_VIEWPORT_HEIGHT, 1));
            ScaleInput.setToolTipText("The scale of the circle");

            Add(new JLabel("Radius:"));
            SameLine();
            Add(RadiusInput);
            SameLine();
            Add(new JLabel("Scale:"));
            SameLine();
            Add(ScaleInput);
            AlignTop();
        }

        /** Get the inputted radius. */
        public int GetRadius() { return (int)RadiusInput.getValue(); }

        /** Get the inputted scale. */
        public int GetScale() { return (int)ScaleInput.getValue(); }
    } private CircleInterfaceControls m_CircleControls;

    /** The interface controls for Rectangles. */
    private class RectangleInterfaceControls extends ShapeInterfaceControls
    {
        /** The input for the width. */
        public JSpinner WidthInput;

        /** The input for the height. */
        public JSpinner HeightInput;

        /** The input for the scale. */
        public JSpinner ScaleInput;

        /** Create components and establish their layouts and styles. */
        public RectangleInterfaceControls()
        {
            super();

            WidthInput = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_WIDTH, 1));
            WidthInput.setToolTipText("The width of the rectangle");

            HeightInput = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_HEIGHT, 1));
            HeightInput.setToolTipText("The height of the rectangle");

            ScaleInput = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_WIDTH * PANEL_VIEWPORT_HEIGHT, 1));
            ScaleInput.setToolTipText("The scale of the rectangle");

            Add(new JLabel("Width:"));
            SameLine();
            Add(WidthInput);
            SameLine();
            Add(new JLabel("Height:"));
            SameLine();
            Add(HeightInput);
            NewLine();
            Add(new JLabel("Scale:"));
            SameLine();
            SpanAvailWidth();
            Add(ScaleInput);
            AlignTop();
        }

        /** Get the inputted width. */
        public int GetWidth() { return (int)WidthInput.getValue(); }

        /** Get the inputted height. */
        public int GetHeight() { return (int)HeightInput.getValue(); }

        /** Get the inputted scale. */
        public int GetScale() { return (int)ScaleInput.getValue(); }
    } private RectangleInterfaceControls m_RectangleControls;

    /** The interface controls for Triangles. */
    private class TriangleInterfaceControls extends ShapeInterfaceControls
    {
        /** The input for the length of side 1. */
        public JSpinner S1Input;

        /** The input for the length of side 2. */
        public JSpinner S2Input;

        /** The input for the length of side 3. */
        public JSpinner S3Input;

        /** The input for the scale. */
        public JSpinner ScaleInput;

        /** Create components and establish their layouts and styles. */
        public TriangleInterfaceControls()
        {
            super();

            S1Input = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_WIDTH, 1));
            S1Input.setToolTipText("The length of side 1 of the triangle");

            S2Input = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_HEIGHT, 1));
            S2Input.setToolTipText("The length of side 2 of the triangle");

            S3Input = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_HEIGHT, 1));
            S3Input.setToolTipText("The length of side 3 of the triangle");

            ScaleInput = new JSpinner(new SpinnerNumberModel(1, 1, PANEL_VIEWPORT_WIDTH * PANEL_VIEWPORT_HEIGHT, 1));
            ScaleInput.setToolTipText("The scale of the triangle");

            Add(new JLabel("S1:"));
            SameLine();
            Add(S1Input);
            SameLine();
            Add(new JLabel("S2:"));
            SameLine();
            Add(S2Input);
            NewLine();
            Add(new JLabel("S3:"));
            SameLine();
            Add(S3Input);
            SameLine();
            Add(new JLabel("Scale:"));
            SameLine();
            Add(ScaleInput);
            AlignTop();
        }

        /** Get the inputted length of side 1. */
        public int GetS1() { return (int)S1Input.getValue(); }

        /** Get the inputted length of side 2. */
        public int GetS2() { return (int)S2Input.getValue(); }

        /** Get the inputted length of side 3. */
        public int GetS3() { return (int)S3Input.getValue(); }

        /** Get the inputted scale. */
        public int GetScale() { return (int)ScaleInput.getValue(); }
    } private TriangleInterfaceControls m_TriangleControls;

    public static void main(String[] args)
    {
        ShapeMaker maker = new ShapeMaker();
        maker.Run();
    }
}
