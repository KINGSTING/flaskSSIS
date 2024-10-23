import re
import mysql.connector
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
                          VALUES (%s, %s, %s, %s, %s, %s, %s)''',
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
            SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, Status = %s
            WHERE IDNumber = %s""",
                       (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, new_status,
                        self.idNumber))
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
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM student WHERE IDNumber = %s", (idNumber,))
        row = cursor.fetchone()
        cursor.close()

        if row:
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

        student = conn.cursor(dictionary=True).execute("SELECT CourseCode FROM student WHERE IDNumber = %s",
                                                       (idNumber,)).fetchone()

        if student:
            course_code = student['CourseCode']
            print(f"Found course code for student {idNumber}: {course_code}")

            program_exists = conn.cursor(dictionary=True).execute("SELECT * FROM program WHERE programCode = %s",
                                                                  (course_code,)).fetchone()

            if not program_exists:
                print(f"Program code {course_code} does not exist. Updating status to 'Unenrolled'.")
                conn.cursor().execute("UPDATE student SET Status = 'Unenrolled' WHERE IDNumber = %s", (idNumber,))
                conn.commit()
                print(f"Student ID {idNumber} status updated to 'Unenrolled'.")
                return True
            else:
                print(f"Program code {course_code} exists. Updating status to 'Enrolled'.")
                conn.cursor().execute("UPDATE student SET Status = 'Enrolled' WHERE IDNumber = %s", (idNumber,))
                conn.commit()
                print(f"Student ID {idNumber} status updated to 'Enrolled'.")
                return True
        else:
            print(f"Student ID {idNumber} not found.")
        return False


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
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM program')
        rows = cursor.fetchall()
        cursor.close()

        # Convert the list of tuples into a list of dictionaries
        programs = []
        for row in rows:
            programs.append({
                'programCode': row[0],
                'programTitle': row[1],
                'programCollege': row[2]
            })

        return programs

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

    def delete_program(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM program WHERE programCode = %s', (self.programCode,))
        self.db.commit()
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
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM college')
        rows = cursor.fetchall()
        cursor.close()

        # Convert the list of tuples into a list of dictionaries
        colleges = []
        for row in rows:
            colleges.append({
                'collegeCode': row[0],
                'collegeName': row[1]
            })
        return colleges

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

    def update_college(self, new_collegeCode, new_collegeName):
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE college 
            SET collegeCode = %s, collegeName = %s 
            WHERE collegeCode = %s
        ''', (new_collegeCode, new_collegeName, self.collegeCode))
        self.db.commit()
        cursor.close()

    def delete_college(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM college WHERE collegeCode = %s', (self.collegeCode,))
        self.db.commit()
        cursor.close()
