/**
 * The entry point of {@link GenericsKbApp} where the {@link KnowledgeBase} is implemented using an array.
 *
 * @see GenericsKbApp
 * @see GenericsKbBSTApp
 * @see KnowledgeBase
 * @see KnowledgeBaseArray
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 03/03/25
 */
public class GenericsKbArrayApp
{
    /**
     * The main function
     *
     * @param args command-line arguments
     */
    public static void main(String[] args)
    {
        GenericsKbApp app = new GenericsKbApp("GenericsKbArrayApp", GenericsKbApp.KnowledgeBaseType.Array);
        app.Run();
    }

    /**
     * Delete the default constructor.
     */
    private GenericsKbArrayApp() { }
}
