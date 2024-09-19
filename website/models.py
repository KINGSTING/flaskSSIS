from . import get_db_connection
from flask import Flask


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
                       (self.idNumber, self.firstName, self.lastName, self.courseCode, self.year, self.gender, self.status))
        self.db.commit()
        cursor.close()

    @staticmethod
    def get_all_students(db_connection):
        cursor = db_connection.cursor()  # Create a cursor
        cursor.execute('SELECT * FROM student')
        students = cursor.fetchall()  # Fetch all students
        cursor.close()
        return students

    @staticmethod
    def find_by_name(db_connection, name):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM student WHERE firstName = ?', (name,))
        student = cursor.fetchone()
        cursor.close()
        return student

    def update_student(self, new_name, new_gender, new_courseCode, new_year):
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE student 
            SET firstName = ?, Gender = ?, CourseCode = ?, Year = ?
            WHERE IDNumber = ?
        ''', (new_name, new_gender, new_courseCode, new_year, self.idNumber))
        self.db.commit()
        cursor.close()
        # Update the object properties
        self.firstName = new_name
        self.gender = new_gender
        self.courseCode = new_courseCode
        self.year = new_year

    def delete(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM student WHERE IDNumber = ?', (self.idNumber,))
        self.db.commit()
        cursor.close()


class Programs:
    def __init__(self, programCode, programTitle, programCollege):
        self.db = get_db_connection()  # Get the database connection
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
    def find_by_code(db_connection, programCode):
        cursor = db_connection.cursor()
        cursor.execute('SELECT * FROM program WHERE programCode = ?', (programCode,))
        program = cursor.fetchone()
        cursor.close()
        return program

    def update_program(self, new_programTitle):
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE program SET programTitle = ? WHERE programCode = ?
        ''', (new_programTitle, self.programCode))
        self.db.commit()
        cursor.close()
        self.programTitle = new_programTitle

    def delete_program(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM program WHERE programCode = ?', (self.programCode,))
        self.db.commit()
        cursor.close()


class Colleges:
    def __init__(self, collegeCode, collegeName):
        self.db = get_db_connection()  # Get the database connection
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
        college = cursor.fetchone()
        cursor.close()
        return college

    def update_college(self, new_collegeName):
        cursor = self.db.cursor()
        cursor.execute(''' 
            UPDATE college SET collegeName = ? WHERE collegeCode = ?
        ''', (new_collegeName, self.collegeCode))
        self.db.commit()
        cursor.close()
        self.collegeName = new_collegeName

    def delete_college(self):
        cursor = self.db.cursor()
        cursor.execute('DELETE FROM college WHERE collegeCode = ?', (self.collegeCode,))
        self.db.commit()
        cursor.close()
