import re
import sqlite3
from . import get_db_connection


class Students:
    def __init__(self, idNumber, firstName, lastName, courseCode, year, gender, status):
        self.db = get_db_connection()
        self.idNumber = idNumber
        self.firstName = firstName
        self.lastName = lastName
        self.courseCode = courseCode
        self.year = year
        self.gender = gender
        self.status = status  # Add status attribute

    def save_student(self):
        cursor = self.db.cursor()
        cursor.execute('''INSERT INTO student (IDNumber, firstName, lastName, CourseCode, Year, Gender, Status) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (self.idNumber, self.firstName, self.lastName, self.courseCode, self.year, self.gender,
                        self.status))
        self.db.commit()
        cursor.close()

    @staticmethod
    def get_all_students(db_connection):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM student')
        students = cursor.fetchall()
        cursor.close()
        return students

    def update_student(self, new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender,
                       new_status):
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE student 
            SET idNumber = ?, firstName = ?, lastName = ?, courseCode = ?, year = ?, gender = ?, status = ?
            WHERE IDNumber = ?""",
                       (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, new_status,
                        self.idNumber))
        self.db.commit()
        cursor.close()

    def check_id_exists(db_connection, idNumber):
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM student WHERE IDNumber = ?", (idNumber,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0  # Returns True if the ID exists, otherwise False

    def validate_id_format(idNumber):
        """
        Validate if the idNumber is in the format YYYY-NNNN.
        """
        pattern = r'^\d{4}-\d{4}$'
        if re.match(pattern, idNumber):
            return True
        else:
            return False

    def delete_student(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM student WHERE IDNumber = ?', (self.idNumber,))
        self.db.commit()
        cursor.close()

    @staticmethod
    def find_by_id(db_connection, idNumber):
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM student WHERE IDNumber = ?", (idNumber,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            # Return the data as a dictionary
            return {
                'IDNumber': row[0],
                'firstName': row[1],
                'lastName': row[2],
                'CourseCode': row[3],
                'Year': row[4],
                'Gender': row[5],
                'Status': row[6],
            }
        return None

    @staticmethod
    def check_and_update_status(conn, idNumber):
        print(f"Checking status for student ID: {idNumber}")

        # Query to get the current program code for the student
        student = conn.execute("SELECT CourseCode FROM student WHERE IDNumber = ?", (idNumber,)).fetchone()

        if student:
            course_code = student['CourseCode']
            print(f"Found course code for student {idNumber}: {course_code}")

            # Check if the program code exists
            program_exists = conn.execute("SELECT * FROM program WHERE programCode = ?", (course_code,)).fetchone()

            if not program_exists:
                print(f"Program code {course_code} does not exist. Updating status to 'Unenrolled'.")
                # Update status to 'Unenrolled' if the program does not exist
                conn.execute("UPDATE student SET Status = 'Unenrolled' WHERE IDNumber = ?", (idNumber,))
                conn.commit()
                print(f"Student ID {idNumber} status updated to 'Unenrolled'.")
                return True  # Indicate that status was updated

            else:
                print(f"Program code {course_code} exists. Updating status to 'Enrolled'.")
                # Update status to 'Enrolled' if the program exists
                conn.execute("UPDATE student SET Status = 'Enrolled' WHERE IDNumber = ?", (idNumber,))
                conn.commit()
                print(f"Student ID {idNumber} status updated to 'Enrolled'.")
                return True  # Indicate that status was updated

        else:
            print(f"Student ID {idNumber} not found.")

        return False  # Indicate that no update was necessary


class Programs:
    def __init__(self, programCode, programTitle, programCollege):
        self.db = get_db_connection()
        self.programCode = programCode
        self.programTitle = programTitle
        self.programCollege = programCollege

    def save_program(self):
        cursor = self.db.cursor()
        cursor.execute(''' 
            INSERT INTO program (programCode, programTitle, programCollege) VALUES (?, ?, ?)
        ''', (self.programCode, self.programTitle, self.programCollege))
        self.db.commit()
        cursor.close()

    @staticmethod
    def get_all_programs(db_connection):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM program')
        programs = cursor.fetchall()
        cursor.close()
        return programs

    @staticmethod
    def find_by_program(db_connection, programCode):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM program WHERE programCode = ?', (programCode,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            # Return the data as a dictionary
            return {
                'programCode': row[0],
                'programTitle': row[1],
                'programCollege': row[2],
            }
        return None

    def update_program(self, conn, new_programCode, new_programTitle, new_collegeCode):
        cursor = conn.cursor()

        cursor.execute(''' 
            UPDATE program 
            SET programCode = ?, programTitle = ?, programCollege = ? 
            WHERE programCode = ? 
        ''', (new_programCode, new_programTitle, new_collegeCode, self.programCode))  # Use self.programCode instead
        conn.commit()  # Commit the changes
        cursor.close()

    def delete_program(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM program WHERE programCode = ?', (self.programCode,))
        self.db.commit()
        cursor.close()

    @staticmethod
    def check_program_exists(db_connection, programCode):
        """
        Check if the programCode already exists in the database.
        """
        cursor = db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM program WHERE programCode = ?", (programCode,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0  # Return True if the programCode exists

    def delete_program_if_college_exists(conn, programCode):
        # Retrieve the program's details
        program = Programs.find_by_program(conn, programCode)

        if program:
            # Check if the program's college exists
            college_exists = Colleges.check_college_exists(conn, program.programCollege)

            if not college_exists:
                # If the college does not exist, delete the program
                conn.execute("DELETE FROM program WHERE programCode = ?", (programCode,))
                conn.commit()
                return f"Program with code {programCode} deleted successfully as the college does not exist."
            else:
                return f"Cannot delete program with code {programCode}: The associated college still exists."
        else:
            return f"Program with code {programCode} not found."

    @staticmethod
    def get_programs_by_college(conn, collegeCode):
        cursor = conn.execute("SELECT * FROM program WHERE collegeCode = ?", (collegeCode,))
        return cursor.fetchall()  # Assuming this returns a list of program objects


class Colleges:
    def __init__(self, collegeCode, collegeName):
        self.db = get_db_connection()
        self.collegeCode = collegeCode
        self.collegeName = collegeName

    def save_college(self):
        cursor = self.db.cursor()
        cursor.execute(''' 
            INSERT INTO college (collegeCode, collegeName) VALUES (?, ?)
        ''', (self.collegeCode, self.collegeName))
        self.db.commit()
        cursor.close()

    @staticmethod
    def get_all_colleges(db_connection):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM college')
        colleges = cursor.fetchall()
        cursor.close()
        return colleges

    @staticmethod
    def find_by_college(db_connection, collegeCode):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM college WHERE collegeCode = ?', (collegeCode,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return {
                'collegeCode': row[0],
                'collegeName': row[1],
                # Add other fields as necessary
            }
        return None

    @staticmethod
    def update_college(conn, originalCollegeCode, new_collegeCode, new_collegeName):
        cursor = conn.cursor()
        cursor.execute(""" 
            UPDATE college 
            SET collegeCode = ?, collegeName = ? 
            WHERE collegeCode = ?
        """, (new_collegeCode, new_collegeName, originalCollegeCode))
        conn.commit()
        cursor.close()

    def delete_college(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: Delete programs associated with this college
        cursor.execute("DELETE FROM program WHERE programCollege = ?", (self.collegeCode,))

        # Step 2: Now delete the college itself
        cursor.execute("DELETE FROM college WHERE collegeCode = ?", (self.collegeCode,))

        # Commit both deletions
        conn.commit()
        cursor.close()

    @staticmethod
    def check_college_exists(conn, college_code):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM college WHERE collegeCode = ?", (college_code,))
        exists = cursor.fetchone()[0] > 0  # Returns True if exists, else False
        cursor.close()
        return exists
