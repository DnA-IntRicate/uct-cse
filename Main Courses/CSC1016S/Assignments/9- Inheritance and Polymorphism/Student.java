/**
 * TODO: Student
 *
 * @author Adam Foflonker (FFLADA001)
 * @version 02/10/24
 */
public class Student extends Person
{
    public Student(String name, int age, String gender, String institution, String studyProgram,
        int yearOfStudy, String hobbies)
        {
            super(name, age, gender);
            m_Institution = institution;
            m_StudyProgram = studyProgram;
            m_YearOfStudy = yearOfStudy;
            m_Hobbies = hobbies;
        }

    public Student(final Student other)
    {
        super(other);

        m_Institution = other.m_Institution;
        m_StudyProgram = other.m_StudyProgram;
        m_YearOfStudy = other.m_YearOfStudy;
        m_Hobbies = other.m_Hobbies;
    }

    public String getNameOfInstitution() { return m_Institution; }
    public void setNameOfInstitution(String institution) { m_Institution = institution; }

    public String getProgramOfStudy() { return m_StudyProgram;}
    public void setProgramOfStudy(String studyProgram) { m_StudyProgram = studyProgram; }

    public int getYearOfStudy() { return m_YearOfStudy; }
    public void setYearOfStudy(int yearOfStudy) { m_YearOfStudy = yearOfStudy; }

    public String getHobbies() { return m_Hobbies; }
    public void setHobbies(String hobbies) { m_Hobbies = hobbies; }

    private String m_Institution;
    private String m_StudyProgram;
    private int m_YearOfStudy;
    private String m_Hobbies;
}
