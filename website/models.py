import re
import mysql.connector
from . import get_db_connection


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

    def save_student(self, conn):
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO student (IDNumber, firstName, lastName, CourseCode, Year, Gender, Status, imageURL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (self.idNumber, self.firstName, self.lastName, self.courseCode, self.year, self.gender, self.status, self.image_url))
            conn.commit()

    @staticmethod
    def get_all_students(db_connection):
        cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor
        cursor.execute('SELECT * FROM student')  # Correct table name
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

    def delete_student(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM student WHERE IDNumber = %s', (self.idNumber,))
        self.db.commit()
        cursor.close()

    @staticmethod
    def find_by_id(db_connection, idNumber):
        cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor
        cursor.execute("SELECT * FROM student WHERE IDNumber = %s", (idNumber,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return row  # Return the dictionary directly
        return None

    @staticmethod
    def check_and_update_status(conn, idNumber):
        print(f"Checking status for student ID: {idNumber}")

        # Ensure the connection and cursor are valid
        cursor = conn.cursor(dictionary=True)

        try:
            # Fetch the student's course code
            cursor.execute("SELECT CourseCode FROM student WHERE IDNumber = %s", (idNumber,))
            student = cursor.fetchone()

            if student:  # Check if a student record was found
                course_code = student['CourseCode']
                print(f"Found course code for student {idNumber}: {course_code}")

                # Check if the program exists
                cursor.execute("SELECT * FROM program WHERE programCode = %s", (course_code,))
                program_exists = cursor.fetchone()

                if not program_exists:  # If no program found, update status to 'Unenrolled'
                    print(f"Program code {course_code} does not exist. Updating status to 'Unenrolled'.")
                    cursor.execute("UPDATE student SET Status = 'Unenrolled' WHERE IDNumber = %s", (idNumber,))
                    conn.commit()
                    print(f"Student ID {idNumber} status updated to 'Unenrolled'.")
                else:  # If program exists, update status to 'Enrolled'
                    print(f"Program code {course_code} exists. Updating status to 'Enrolled'.")
                    cursor.execute("UPDATE student SET Status = 'Enrolled' WHERE IDNumber = %s", (idNumber,))
                    conn.commit()
                    print(f"Student ID {idNumber} status updated to 'Enrolled'.")
            else:
                print(f"Student ID {idNumber} not found.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            # Close the cursor after the operation
            cursor.close()


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
