/**
 * The entry point of {@link GenericsKbApp} where the {@link KnowledgeBase} is implemented using a {@link BinarySearchTree}.
 *
 * @see GenericsKbApp
 * @see GenericsKbArrayApp
 * @see KnowledgeBase
 * @see KnowledgeBaseBST
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 07/03/25
 */
public class GenericsKbBSTApp
{
    /**
     * The main function
     *
     * @param args command-line arguments
     */
    public static void main(String[] args)
    {
        GenericsKbApp app = new GenericsKbApp("GenericsKbBSTApp", GenericsKbApp.KnowledgeBaseType.BinarySearchTree);
        app.Run();
    }

    /**
     * Delete the default constructor.
     * If only Java allowed the declaration of static classes like C#...
     */
    private GenericsKbBSTApp() { }
}
