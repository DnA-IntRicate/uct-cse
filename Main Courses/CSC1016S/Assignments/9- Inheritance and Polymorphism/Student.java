/**
 * Stores the information of a student for use in {@link Question3}. Inherits from {@link Person}.
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Student extends Person
{
    /**
     * Create a new {@link Student} with the given student information.
     *
     * @param name the name of the student
     * @param age the age of the student
     * @param gender the gender of the student
     * @param institution the institution of study of the student
     * @param studyProgram the study program of the student
     * @param yearOfStudy the year of study of the student
     * @param hobbies the hobbies of the student
     */
    public Student(String name, int age, String gender, String institution, String studyProgram,
        int yearOfStudy, String hobbies)
        {
            super(name, age, gender);
            m_Institution = institution;
            m_StudyProgram = studyProgram;
            m_YearOfStudy = yearOfStudy;
            m_Hobbies = hobbies;
        }

    /**
     * Copy constructor.
     *
     * @param other the {@link Student} to copy
     */
    public Student(final Student other)
    {
        super(other);

        m_Institution = other.m_Institution;
        m_StudyProgram = other.m_StudyProgram;
        m_YearOfStudy = other.m_YearOfStudy;
        m_Hobbies = other.m_Hobbies;
    }

    /**
     * Get the institution of study of this student.
     *
     * @return the institution of study of this student
     */
    public String getNameOfInstitution() { return m_Institution; }

    /**
     * Set the institution of study of this student.
     *
     * @param institution the new institution to set
     */
    public void setNameOfInstitution(String institution) { m_Institution = institution; }

    /**
     * Get the program of study of this student.
     *
     * @return the program of study of this student
     */
    public String getProgramOfStudy() { return m_StudyProgram;}

    /**
     * Set the program of study of this student.
     *
     * @param studyProgram the new program of study to set
     */
    public void setProgramOfStudy(String studyProgram) { m_StudyProgram = studyProgram; }

    /**
     * Get the year of study of this student.
     *
     * @return the year of study of this student
     */
    public int getYearOfStudy() { return m_YearOfStudy; }

    /**
     * Set the year of study of this student.
     *
     * @param yearOfStudy the new year of study to set
     */
    public void setYearOfStudy(int yearOfStudy) { m_YearOfStudy = yearOfStudy; }

    /**
     * Get the hobbies of this student.
     *
     * @return the hobbies of this student
     */
    public String getHobbies() { return m_Hobbies; }

    /**
     * Set the hobbies of this student.
     *
     * @param hobbies the new hobbies to set
     */
    public void setHobbies(String hobbies) { m_Hobbies = hobbies; }

    // This student's institution of study.
    private String m_Institution;

    // This student's study program.
    private String m_StudyProgram;

    // This student's year of study.
    // NOTE: This field is not currently used by the Question3 program.
    private int m_YearOfStudy;

    // This student's hobbies.
    private String m_Hobbies;
}
