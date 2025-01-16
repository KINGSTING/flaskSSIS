import re
import mysql.connector
from website import get_db_connection


class Students:
    def __init__(self, idNumber, firstName, lastName, courseCode, year, gender, status, image_url=None):
        self.idNumber = idNumber
        self.firstName = firstName
        self.lastName = lastName
        self.courseCode = courseCode
        self.year = year
        self.gender = gender
        self.status = status
        self.image_url = image_url  # New field for the image URL
        self.db = get_db_connection()

    def save_student(self, conn):
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO student (IDNumber, firstName, lastName, CourseCode, Year, Gender, Status, imageURL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.idNumber, self.firstName, self.lastName, self.courseCode, self.year, self.gender, self.status, self.image_url))
            conn.commit()

    @staticmethod
    def get_all_students(db_connection, offset, per_page):
        cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor
        cursor.execute('SELECT * FROM student LIMIT %s OFFSET %s',
                       (per_page, offset))  # Add LIMIT and OFFSET for pagination
        students = cursor.fetchall()
        cursor.close()
        return students

    def update_student(self, new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender,
                       new_status, new_image_url=None):
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE student 
            SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, Status = %s, imageURL = %s
            WHERE IDNumber = %s""",
                       (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, new_status, new_image_url, self.idNumber))
        self.db.commit()
        cursor.close()

    @staticmethod
    def check_id_exists(db_connection, idNumber):
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM student WHERE IDNumber = %s", (idNumber,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0  # Returns True if the ID exists, otherwise False

    @staticmethod
    def validate_id_format(idNumber):
        """
        Validate if the idNumber is in the format YYYY-NNNN.
        """
        pattern = r'^\d{4}-\d{4}$'
        return re.match(pattern, idNumber) is not None

    def delete_student(self, conn):
        cursor = conn.cursor()
        cursor.execute('DELETE FROM student WHERE IDNumber = %s', (self.idNumber,))
        conn.commit()
        cursor.close()

    @staticmethod
    def find_by_id(db_connection, idNumber):
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT * FROM student WHERE IDNumber = %s", (idNumber,))
            row = cursor.fetchone()
            cursor.close()

            if row:
                # Assuming the order of columns in the "student" table:
                # (idNumber, firstName, lastName, courseCode, year, gender, status, image_url)
                return Students(
                    idNumber=row[0],
                    firstName=row[1],
                    lastName=row[2],
                    courseCode=row[3],
                    year=row[4],
                    gender=row[5],
                    status=row[6],
                    image_url=row[7] if len(row) > 7 else None
                )
            print("No matching student found.")
            return None
        except Exception as e:
            print(f"Error in find_by_id: {e}")
            return None

    @staticmethod
    def check_and_update_status(conn, idNumber):

        # Ensure the connection and cursor are valid
        cursor = conn.cursor(dictionary=True)

        try:
            # Fetch the student's course code
            cursor.execute("SELECT CourseCode FROM student WHERE IDNumber = %s", (idNumber,))
            student = cursor.fetchone()

            if student:  # Check if a student record was found
                course_code = student['CourseCode']

                # Check if the program exists
                cursor.execute("SELECT * FROM program WHERE programCode = %s", (course_code,))
                program_exists = cursor.fetchone()

                if not program_exists:  # If no program found, update status to 'Unenrolled'
                    cursor.execute("UPDATE student SET Status = 'Unenrolled' WHERE IDNumber = %s", (idNumber,))
                    conn.commit()
                else:  # If program exists, update status to 'Enrolled'
                    cursor.execute("UPDATE student SET Status = 'Enrolled' WHERE IDNumber = %s", (idNumber,))
                    conn.commit()

            else:
                print(f"Student ID {idNumber} not found.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            # Close the cursor after the operation
            cursor.close()

    @staticmethod
    def get_student_count(db_connection):
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM student")
            count = cursor.fetchone()[0]  # Fetch the first value of the result tuple
            cursor.close()
            return count
        except mysql.connector.Error as err:
            print(f"Error fetching student count: {err}")
            return None

    @staticmethod
    def update_student_info(db_connection, new_idNumber, new_firstName, new_lastName, new_courseCode, new_year,
                            new_gender, new_image_url=None, current_idNumber=None):
        with db_connection.cursor() as cursor:
            sql = """
                UPDATE student 
                SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, imageURL = %s 
                WHERE IDNumber = %s
            """
            # Use the provided current_idNumber (which is the original ID number of the student)
            cursor.execute(sql, (
                new_idNumber,
                new_firstName,
                new_lastName,
                new_courseCode,
                new_year,
                new_gender,
                new_image_url,
                current_idNumber  # Existing IDNumber of the student
            ))
            db_connection.commit()

    @staticmethod
    def search_student_by_id(db_connection, id_number):
        query = "SELECT * FROM student WHERE LOWER(IDNumber) LIKE LOWER(%s)"
        try:
            with db_connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, (id_number.strip(),))  # Ensure parameter is a tuple (id_number,)
                result = cursor.fetchone()  # Fetch a single record or None
            return result  # Return the student record or None if not found
        except Exception as e:
            print(f"Error while searching for student by ID: {e}")
            return None

    @staticmethod
    def search_student_by_gender(conn, gender):

        query = """
               SELECT * FROM student 
               WHERE LENGTH(Gender) = LENGTH(TRIM(%s)) 
               AND LOWER(Gender) = LOWER(TRIM(%s))
           """
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, (gender.strip(), gender.strip()))
                results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error searching for students by gender: {e}")
            return []

    @staticmethod
    def search_student_by_field(db_connection, search_field, search_value):
        # Mapping of allowed search fields to database columns
        field_map = {
            'idNumber': 'IDNumber',
            'firstName': 'firstName',
            'lastName': 'lastName',
            'course': 'CourseCode',
            'yearLevel': 'Year',
            'gender': 'Gender',
            'status': 'Status'
        }

        # Validate the search field
        if search_field not in field_map:
            raise ValueError(f"Invalid search field: {search_field}")

        # Prepare the SQL query for partial match using LIKE
        query = f"SELECT * FROM student WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"

        try:
            with db_connection.cursor(dictionary=True) as cursor:
                # Parameterized query to prevent SQL injection
                cursor.execute(query, (f"%{search_value.strip()}%",))  # Using % for partial match
                results = cursor.fetchall()  # Fetch all matching records
            return results  # Return the list of students found, or empty list if no match
        except Exception as e:
            print(f"Error while searching for student by {search_field}: {e}")
            return []  # Return an empty list in case of any errors



class Programs:
    def __init__(self, programCode, programTitle, programCollege):
        self.db = get_db_connection()
        self.programCode = programCode
        self.programTitle = programTitle
        self.programCollege = programCollege

    def save_program(self):
        cursor = self.db.cursor()
        cursor.execute(''' 
            INSERT INTO program (programCode, programTitle, programCollege) VALUES (%s, %s, %s)
        ''', (self.programCode, self.programTitle, self.programCollege))
        self.db.commit()
        cursor.close()

    @staticmethod
    def get_all_programs(db_connection):
        cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor
        cursor.execute('SELECT * FROM program')
        rows = cursor.fetchall()
        cursor.close()
        return rows  # Return the list of dictionaries

    @staticmethod
    def find_by_program(db_connection, programCode):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM program WHERE programCode = %s', (programCode,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Programs(row[0], row[1], row[2])
        return None

    @staticmethod
    def search_program_by_field(db_connection, search_field, search_value):
        # Validate input
        if not search_value or not search_field:
            raise ValueError("Search field and value must be provided.")

        # Mapping of allowed search fields to database columns
        field_map = {
            'programCode': 'programCode',
            'programTitle': 'programTitle',
            'programCollege': 'programCollege'
        }

        # Validate the search field
        if search_field not in field_map:
            raise ValueError(f"Invalid search field: {search_field}")

        # Prepare the SQL query for partial match using LIKE
        query = f"SELECT * FROM program WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"

        try:
            with db_connection.cursor(dictionary=True) as cursor:
                # Parameterized query to prevent SQL injection
                cursor.execute(query, (f"%{search_value.strip()}%",))  # Using % for partial match
                results = cursor.fetchall()  # Fetch all matching records
            return results  # Return the list of programs found, or empty list if no match
        except Exception as e:
            print(f"Error while searching for program by {search_field}: {e}")
            return []  # Return an empty list in case of any errors

    def update_program(self, conn, new_programCode, new_programTitle, new_collegeCode):
        cursor = conn.cursor()
        cursor.execute(''' 
            UPDATE program 
            SET programCode = %s, programTitle = %s, programCollege = %s 
            WHERE programCode = %s 
        ''', (new_programCode, new_programTitle, new_collegeCode, self.programCode))
        conn.commit()
        cursor.close()

    @classmethod
    def delete_program(cls, conn, program_code):
        pass
        cursor = conn.cursor()
        cursor.execute("DELETE FROM program WHERE programCode = %s", (program_code,))
        conn.commit()
        cursor.close()

    @staticmethod
    def check_program_exists(db_connection, programCode):
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM program WHERE programCode = %s", (programCode,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0

    @staticmethod
    def delete_program_if_college_exists(conn, programCode):
        program = Programs.find_by_program(conn, programCode)
        if program:
            college_exists = Colleges.check_college_exists(conn, program.programCollege)
            if not college_exists:
                conn.cursor().execute("DELETE FROM program WHERE programCode = %s", (programCode,))
                conn.commit()
                return f"Program with code {programCode} deleted successfully as the college does not exist."
            else:
                return f"Cannot delete program with code {programCode}: The associated college still exists."
        else:
            return f"Program with code {programCode} not found."

    @staticmethod
    def get_programs_by_college(conn, collegeCode):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM program WHERE programCollege = %s", (collegeCode,))
        return cursor.fetchall()


class Colleges:
    def __init__(self, collegeCode, collegeName):
        self.db = get_db_connection()
        self.collegeCode = collegeCode
        self.collegeName = collegeName

    def save_college(self):
        cursor = self.db.cursor()
        cursor.execute(''' 
            INSERT INTO college (collegeCode, collegeName) VALUES (%s, %s)
        ''', (self.collegeCode, self.collegeName))
        self.db.commit()
        cursor.close()

    @staticmethod
    def get_all_colleges(db_connection):
        cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor
        cursor.execute('SELECT * FROM college')
        rows = cursor.fetchall()
        cursor.close()
        return rows  # Return the list of dictionaries

    @staticmethod
    def check_college_exists(db_connection, collegeCode):
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM college WHERE collegeCode = %s", (collegeCode,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0  # Returns True if the college exists, otherwise False

    @staticmethod
    def find_by_college(db_connection, collegeCode):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM college WHERE collegeCode = %s', (collegeCode,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Colleges(row[0], row[1])
        return None

    @staticmethod
    def search_college_by_field(db_connection, search_field, search_value):
        # Validate input
        if not search_value or not search_field:
            raise ValueError("Search field and value must be provided.")

        # Mapping of allowed search fields to database columns
        field_map = {
            'collegeCode': 'collegeCode',
            'collegeName': 'collegeName',
        }

        # Validate the search field
        if search_field not in field_map:
            raise ValueError(f"Invalid search field: {search_field}")

        # Prepare the SQL query for partial match using LIKE
        query = f"SELECT * FROM college WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"

        try:
            with db_connection.cursor(dictionary=True) as cursor:
                # Parameterized query to prevent SQL injection
                cursor.execute(query, (f"%{search_value.strip()}%",))  # Using % for partial match
                results = cursor.fetchall()  # Fetch all matching records
            return results  # Return the list of colleges found, or empty list if no match
        except Exception as e:
            print(f"Error while searching for college by {search_field}: {e}")
            return []  # Return an empty list in case of any errors

    @staticmethod
    def update_college(conn, new_college_code, new_college_name):
        cursor = conn.cursor()  # Use the passed connection directly
        cursor.execute("""UPDATE college 
                          SET collegeName = %s 
                          WHERE collegeCode = %s""",
                       (new_college_name, new_college_code))
        conn.commit()  # Commit the changes on the connection
        cursor.close()  # Always close the cursor

    def delete_college(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM college WHERE collegeCode = %s', (self.collegeCode,))
        self.db.commit()
        cursor.close()
