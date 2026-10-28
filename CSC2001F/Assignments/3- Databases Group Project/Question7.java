import java.sql.*;
import java.util.Scanner;

/**
 * Solution to question 7 of CSC2001F-2025 DB3 Assignment
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 14/05/25
 */
public class Question7
{
    public static void main(String[] args)
    {
        // TODO(Adam): This connection string isn't fully correct, mainly here for demonstration-purposes
        // Fixed - Kieran

        String username;
        String password;   // Lol I'm not giving you my password :)
        String database;

        // Allow command-line argument OR fall back to user input
        if (args.length >= 3)
        {
            username = args[0];
            password = args[1];
            database = args[2];
        }
        else
        {
            Scanner varScanner = new Scanner(System.in);
            System.out.print("Enter MySQL username: ");
            username = varScanner.nextLine();
            System.out.print("Enter MySQL password: ");
            password = varScanner.nextLine();
            System.out.println("Enter database name (default is student number): ");
            database = varScanner.nextLine();

            varScanner.close();
        }

        //localhost:3306/cs";//
        String connStr = "jdbc:mysql://" + username + "@nightmare.cs.uct.ac.za:3306/" + database;

        try
        (
            Connection conn = DriverManager.getConnection(connStr, username, password);
            Statement stmt = conn.createStatement()
        )
        {
            stmt.executeUpdate("""
                CREATE TABLE IF NOT EXISTS Assessment
                (
                    course_id VARCHAR(10),
                    assessment_id VARCHAR(10),
                    title VARCHAR(100),
                    max_score INT,
                    description TEXT,
                    start_date DATE,
                    end_date DATE,
                    PRIMARY KEY (course_id, assessment_id)
                )""");
            System.out.println("\nTable 'Assessment' created.");

            String insertQueryStub = """
                INSERT INTO Assessment (course_id, assessment_id, title, max_score, description, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)""";

            try (PreparedStatement pstmt = conn.prepareStatement(insertQueryStub)) {
                pstmt.setString(1, "CSC2001F");
                pstmt.setString(2, "A1");
                pstmt.setString(3, "DS1");
                pstmt.setInt(4, 10);
                pstmt.setString(5, "First data structures assignment.");
                pstmt.setDate(6, Date.valueOf("2025-06-01"));
                pstmt.setDate(7, Date.valueOf("2025-06-03"));
                pstmt.executeUpdate();

                pstmt.setString(1, "CSC2001F");
                pstmt.setString(2, "A2");
                pstmt.setString(3, "DS2");
                pstmt.setInt(4, 20);
                pstmt.setString(5, "Second data structures assignment.");
                pstmt.setDate(6, Date.valueOf("2025-06-05"));
                pstmt.setDate(7, Date.valueOf("2025-06-10"));
                pstmt.executeUpdate();

                pstmt.setString(1, "CSC2001F");
                pstmt.setString(2, "Q1");
                pstmt.setString(3, "DS3");
                pstmt.setInt(4, 40);
                pstmt.setString(5, "Data structures quiz.");
                pstmt.setDate(6, Date.valueOf("2025-06-15"));
                pstmt.setDate(7, Date.valueOf("2025-06-15"));
                pstmt.executeUpdate();
            }

            // Retrieval example with assessment_id 'A2'
            ResultSet rs = stmt.executeQuery("SELECT * FROM Assessment WHERE course_id = 'CSC2001F' AND assessment_id = 'A2'");
            if (rs.next())
            {
                System.out.println("\nRetrieved Row:");
                System.out.println("Course ID: " + rs.getString("course_id"));
                System.out.println("Assessment ID: " + rs.getString("assessment_id"));
                System.out.println("Title: " + rs.getString("title"));
                System.out.println("Max Score: " + rs.getInt("max_score"));
                System.out.println("Description: " + rs.getString("description"));
                System.out.println("Start Date: " + rs.getDate("start_date"));
                System.out.println("End Date: " + rs.getDate("end_date"));
            }
        }
        catch (SQLException e)
        {
            e.printStackTrace();
        }
    }
}
