package SoloLeveling.Parallel;

import java.io.File;
import java.util.Random;
import java.awt.Color;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

/**
 * Implementation of {@link SoloLeveling.Serial.DungeonMap} for use in {@link DungeonHunterParallel}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 15/08/2025
 */
public class DungeonMapParallel
{
    /**
     * Creates a new {@link DungeonMapParallel}.
     *
     * @param xMin the minimum x-coordinate
     * @param xMax the maximum x-coordinate
     * @param yMin the minimum y-coordinate
     * @param yMax the maximum y-coordinate
     * @param seed the random seed defining where the boss peak is placed in the dungeon map
     */
    public DungeonMapParallel(double xMin, double xMax, double yMin, double yMax, int seed)
    {
        m_XMin = xMin;
        m_XMax = xMax;
        m_YMin = yMin;
        m_YMax = yMax;

        // The grid resolution is constant
        m_Rows = (int)Math.round((m_XMax - m_XMin) * RESOLUTION);
        m_Columns = (int)Math.round((m_YMax - m_YMin) * RESOLUTION);

        // Randomly place the boss peak
        Random rand = (seed == 0) ? new Random() : new Random(seed);

        double xRange = m_XMax - m_XMin;
        double yRange = m_YMax - m_YMin;

        m_BossX = m_XMin + (xRange * rand.nextDouble());
        m_BossY = m_YMin + (yRange * rand.nextDouble());

        // Calculate decay factor based on range
        // m_DecayFactor = 2.0 / (xRange * 0.1);

        m_ManaMap = new int[m_Rows][m_Columns];
        m_Visit = new int[m_Rows][m_Columns];
        m_DungeonGridPointsEvaluated = 0;

        // Terrain initialization
        for(int i = 0; i < m_Rows; ++i)
        {
            for(int j = 0; j < m_Columns; ++j)
            {
                m_ManaMap[i][j] = Integer.MIN_VALUE; // Mana not yet measured
                m_Visit[i][j] = -1; // Grid point not yet visited
            }
        }
    }

    /**
     * Has this cell been visited yet?
     *
     * @return {@code true} if this cell has been visited, {@code false} otherwise
    */
    boolean Visited(int x, int y) { return m_Visit[x][y] != -1; }

    /**
     * Mark the cell at coordinates {@code x} and {@code y} as visited.
     *
     * @param x the x-coordinate of the cell
     * @param y the y-coordinate of the cell
     * @param id the ID of the hunt that visited the cell
     */
    void SetVisited(int x, int y, int id)
    {
        if (!Visited(x, y))
            m_Visit[x][y] = id;
    }

    /**
    * Evaluates mana at a {@link DungeonGridParallel} coordinate (x, y) in the dungeon,
    * and writes it to the map.
    *
    * @param x The x-coordinate in the dungeon grid.
    * @param y The y-coordinate in the dungeon grid.
    * @return an int value representing the mana level at (x, y).
    */
    int GetManaLevel(int x, int y)
    {
        if (Visited(x,y))
            return m_ManaMap[x][y];

        if (m_ManaMap[x][y] > Integer.MIN_VALUE)
            return m_ManaMap[x][y];  // Return value if it was already calculated

        // Calculate the coordinates of the point in the ranges
        double xCoord = m_XMin + ((m_XMax - m_XMin) / m_Rows) * x;
        double yCoord = m_YMin + ((m_YMax - m_YMin) / m_Columns) * y;
        double dx = xCoord - m_BossX;
        double dy = yCoord - m_BossY;
        double distanceSquared = dx * dx + dy * dy;

        // Computing the mana value. DO NOT CHANGE
        double mana = (2 * Math.sin(xCoord + 0.1 * Math.sin(yCoord / 5.0) + Math.PI / 2) *
                Math.cos((yCoord + 0.1 * Math.cos(xCoord / 5.0) + Math.PI / 2) / 2.0) +
            0.7 * Math.sin((xCoord * 0.5) + (yCoord * 0.3) + 0.2 * Math.sin(xCoord / 6.0) + Math.PI / 2) +
            0.3 * Math.sin((xCoord * 1.5) - (yCoord * 0.8) + 0.15 * Math.cos(yCoord / 4.0)) +
            -0.2 * Math.log(Math.abs(yCoord - Math.PI * 2) + 0.1) +
            0.5 * Math.sin((xCoord * yCoord) / 4.0 + 0.05 * Math.sin(xCoord)) +
            1.5 * Math.cos((xCoord + yCoord) / 5.0 + 0.1 * Math.sin(yCoord)) +
            3.0 * Math.exp(-0.03 * ((xCoord - m_BossX - 15) * (xCoord - m_BossX - 15) +
                                    (yCoord - m_BossY + 10) * (yCoord - m_BossY + 10))) +
            8.0 * Math.exp(-0.01 * distanceSquared) +
            2.0 / (1.0 + 0.05 * distanceSquared));

        // Transform to fixed point precision
        int fixedPoint = (int)(PRECISION * mana);
        m_ManaMap[x][y] = fixedPoint;
        m_DungeonGridPointsEvaluated++;

        return fixedPoint;
    }

     /**
     * Returns the direction of the neighbouring cell with the highest mana
     *
     * @param x The x-coordinate in the dungeon grid
     * @param y The y-coordinate in the dungeon grid
     * @return the direction of highest mana
     */
    HuntParallel.Direction GetNextStepDirection(int x, int y)
    {
        HuntParallel.Direction res = HuntParallel.Direction.Stay;
        int localMax = GetManaLevel(x, y);

        // Define directions with (dx, dy)
        int[][] directions =
        {
            {-1,  0}, // Left
            { 1,  0}, // Right
            { 0, -1}, // Up
            { 0,  1}, // Down
            {-1, -1}, // UpLeft
            { 1, -1}, // UpRight
            {-1,  1}, // DownLeft
            { 1,  1}  // DownRight
        };

        HuntParallel.Direction[] directionEnums =
        {
            HuntParallel.Direction.Left,
            HuntParallel.Direction.Right,
            HuntParallel.Direction.Up,
            HuntParallel.Direction.Down,
            HuntParallel.Direction.UpLeft,
            HuntParallel.Direction.UpRight,
            HuntParallel.Direction.DownLeft,
            HuntParallel.Direction.DownRight
        };

        for (int i = 0; i < directions.length; ++i)
        {
            int newX = x + directions[i][0];
            int newY = y + directions[i][1];

            if ((newX >= 0) && (newX < m_Rows) && (newY >= 0) && (newY < m_Columns))
            {
                int power = GetManaLevel(newX, newY);
                if (power > localMax)
                {
                    localMax = power;
                    res = directionEnums[i];
                }
            }
        }

        return res;
    }

    /**
     * Generates an image from the dungeon grid.
     * Unvisited cells are colored black, while visited cells follow a black->purple->red->white gradient.
     *
     * @param filename The name of the output PNG file
     */
    public void VisualisePowerMap(String filename, boolean path)
    {
        int width = m_ManaMap.length;
        int height = m_ManaMap[0].length;

        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);

        // Find min and max for normalization (ignore unvisited sites)
        int min = Integer.MAX_VALUE;
        int max = Integer.MIN_VALUE;

        for (int x = 0; x < width; ++x)
        {
            for (int y = 0; y < height; ++y)
            {
                int value = m_ManaMap[x][y];
                if (value == Integer.MIN_VALUE)
                    continue;

                if (value < min)
                    min = value;

                if (value > max)
                    max = value;
            }
        }

        // Prevent division by zero if everything has the same value
        double range = (max > min) ? (max - min) : 1.0;

        // Map height values to colors
        for (int x = 0; x < width; ++x)
        {
            for (int y = 0; y < height; ++y)
            {
                Color color;

                if (path && !Visited(x, y))
                    color = Color.BLACK;
                else if (m_ManaMap[x][y] == Integer.MIN_VALUE)
                    color = Color.BLACK;
                else
                {
                    double normalized = (m_ManaMap[x][y] - min) / range; // 0-1
                    color = MapHeightToColor(normalized);
                }

                image.setRGB(x, height - 1 - y, color.getRGB());
            }
        }

        try
        {
            File output = new File(filename);
            ImageIO.write(image, "png", output);
            System.out.println("map saved to " + filename);
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }

    /**
     * Returns the number of grid points evaluated.
     * @return the number of grid points evaluated
     */
    public int GetGridPointsEvaluated() { return m_DungeonGridPointsEvaluated; }

    /**
     * Returns the given x-coordinate in terms of this dungeon map
     * @param x
     * @return the x-coordinate in terms of this dungeon map
     */
    public double GetXcoord(int x) { return m_XMin + ((m_XMax - m_XMin) / m_Rows) * x; }

    /**
     * Returns the given y-coordinate in terms of this dungeon map
     * @param y
     * @return the y-coordinate in terms of this dungeon map
     */
    public double GetYcoord(int y) { return m_YMin + ((m_YMax - m_YMin) / m_Columns) * y; }

    /**
     * Returns the number of rows in this dungeon map.
     *
     * @return the number of rows in this dungeon map
     */
    public int GetRows() { return m_Rows; }

    /**
     * Returns the number of columns in this dungeon map.
     *
     * @return the number of columns in this dungeon map
     */
    public int GetColumns() { return m_Columns; }

    /** Maps normalized height [0..1] to black -> purple -> red -> white */
    private Color MapHeightToColor(double normalized)
    {
        normalized = Math.max(0, Math.min(1, normalized)); // Clamp to [0,1]

        int r = 0, g = 0, b = 0;
        if (normalized < 0.33)
        {
            // Black -> Purple
            double t = normalized / 0.33;
            r = (int)(128 * t); // Purple has some red
            g = 0;
            b = (int)(128 + 127 * t); // Increasing blue
        }
        else if (normalized < 0.66)
        {
            // Purple -> Red
            double t = (normalized - 0.33) / 0.33;
            r = (int)(128 + 127 * t); // Red dominates
            g = 0;
            b = (int)(255 - 255 * t); // Fade out blue
        }
        else
        {
            // Red -> White
            double t = (normalized - 0.66) / 0.34;
            r = 255;
            g = (int)(255 * t);
            b = (int)(255 * t);
        }

        return new Color(r, g, b);
    }

    /** Grid precision */
    public static final int PRECISION = 10000;

    /** Grid resolution */
    public static final int RESOLUTION = 5;

    // Number of rows in the dungeon grid
    private int m_Rows = 0;

    // Number of columns in the dungeon grid
    private int m_Columns = 0;

    // X minimum limit
    private double m_XMin = 0.0;

    // X maximum limit
    private double m_XMax = 0.0;

    // Y minimum limit
    private double m_YMin = 0.0;

    // Y maximum limit
    private double m_YMax = 0.0;

    // The mana map represented as a 2D array
    private int[][] m_ManaMap;

    // The map of all visited cells in the dungeon grid
    private int[][] m_Visit;

    // The number of dungeon grid points that have been evaluated
    private int m_DungeonGridPointsEvaluated = 0;

    // The x-coordinate of the boss peak in the dungeon grid
    private double m_BossX = 0.0;

    // The y-coordinate of the boss peak in the dungeon grid
    private double m_BossY = 0.0;

    // Have no idea what this is for but hey, its here...
    // private double m_DecayFactor = 0.0;
}
