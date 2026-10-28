/**
 * Why the heck does Java not have a Tuple or Pair class already?
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 01/03/25
 */
public class Pair <_Ty1, _Ty2>
{
    public Pair(_Ty1 first, _Ty2 second)
    {
        First = first;
        Second = second;
    }

    public _Ty1 First;
    public _Ty2 Second;
}
