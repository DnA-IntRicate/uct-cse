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
    }

    public void Initialize()
    {
        setSize(800, 600);
        setLayout(new FlowLayout());
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);

        add(m_ShapesComboBox);
        add(m_DrawShapeButton);
        add(m_ColorsComboBox);

        add(m_RectWidthInput);
        add(m_RectHeightInput);

        setVisible(true);
    }

    // TODO: Draw this on a separate panel (JPanel)
    public void DrawRectangle(final Rectangle rect, int x, int y)
    {
        Log("Drawing Rectangle: " + rect.toString());

        Graphics2D g = (Graphics2D)getGraphics();
        g.setColor(Utils.StrColorToColor(rect.getColor()));

        if (rect.isFilled())
            g.fillRect(x, y, (int)rect.getWidth(), (int)rect.getHeight());
        else
            g.drawRect(x, y, (int)rect.getWidth(), (int)rect.getHeight());

        // Enable anti-aliasing for smoother shapes
      //  g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

      //  // Set color and draw a filled circle (oval)
      //  g2d.setColor(Color.RED);
      //  g2d.fillOval(50, 50, 100, 100); // (x, y, width, height)
//
      //  // Set color and draw a filled rectangle
      //  g2d.setColor(Color.BLUE);
      //  g2d.fillRect(200, 50, 150, 100); // (x, y, width, height)
//
      //  // Set color and draw a triangle (polygon with 3 points)
      //  g2d.setColor(Color.GREEN);
      //  int[] xPoints = {400, 450, 500}; // X coordinates of the triangle vertices
      //  int[] yPoints = {150, 50, 150};  // Y coordinates of the triangle vertices
      //  g2d.fillPolygon(xPoints, yPoints, 3); // Number of points = 3 for a triangle

     //   paintComponents(g2d);
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

    private JSpinner m_RectWidthInput;
    private JSpinner m_RectHeightInput;

    // TODO: Create a label with the text "Dimensions" and under it put all shape dimension stuff
}
