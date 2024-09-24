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

    def update_student(self, new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, new_status):
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE student 
            SET idNumber = ?, firstName = ?, lastName = ?, courseCode = ?, year = ?, gender = ?, status = ?
            WHERE IDNumber = ?""",
                       (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, new_status, self.idNumber))
        self.db.commit()
        cursor.close()

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
        return Students(*row) if row else None  # Return an instance if found

    def set_status_based_on_program(self, conn):
        cursor = conn.cursor()

        # Check if the programCode exists in the Programs table
        cursor.execute("SELECT * FROM program WHERE programCode = ?", (self.courseCode,))
        program = cursor.fetchone()

        if program:
            # If program exists, set status to 'Enrolled'
            self.status = "Enrolled"
        else:
            # If program does not exist, set status to 'Unenrolled'
            self.status = "Unenrolled"

        # Commit status change to the database
        cursor.execute("""
            UPDATE student
            SET Status = ?
            WHERE IDNumber = ?
        """, (self.status, self.idNumber))
        conn.commit()

        # Return the updated status
        return self.status


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
        return Programs(*row) if row else None  # Return an instance if found

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
        return Colleges(*row) if row else None  # Return an instance if found

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
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM college WHERE collegeCode = ?', (self.collegeCode,))
        self.db.commit()
        cursor.close()
