import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for
from .models import Students, Programs, Colleges
from . import get_db_connection  # Import your connection function

views = Blueprint("views", __name__)


# Define the route for the home page
@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")


@views.route('/students', methods=['GET'])
def view_students():
    # Fetch all students
    students = Students.get_all_students(get_db_connection())

    # Fetch all programs for the course selection
    programs = Programs.get_all_programs(get_db_connection())

    return render_template('student.html', students=students, programs=programs)


# Define the route for the program page
@views.route('/programs', methods=['GET'])
def view_programs():
    # Fetch all programs
    programs = Programs.get_all_programs(get_db_connection())

    # Fetch all colleges for the combo box
    colleges = Colleges.get_all_colleges(get_db_connection())

    return render_template('program.html', programs=programs, colleges=colleges)


# Define the route for the college page
@views.route("/colleges")
def collegePage():
    conn = get_db_connection()
    all_colleges = Colleges.get_all_colleges(conn)
    conn.close()
    return render_template("college.html", colleges=all_colleges)


@views.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == "POST":
        idNumber = request.form.get("idNumber")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        courseCode = request.form.get("courseCode")
        year = request.form.get("year")
        gender = request.form.get("gender")

        # Check if the courseCode exists in the programs
        program = Programs.find_by_code(get_db_connection(), courseCode)

        # Set status based on whether the courseCode exists
        if program:
            status = "Enrolled"
        else:
            status = "Unenrolled"

        # Create a new student instance
        new_student = Students(idNumber, firstName, lastName, courseCode, year, gender, status)
        new_student.status = status  # Set the status attribute

        # Save the student to the database
        new_student.save_student()

        # Optionally, redirect or return a success message
        return redirect('/students')  # Redirect to a page showing students

    return render_template('add_student.html')  # Render the form again if GET request


@views.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    # Find and delete the student by ID number
    student = Students(idNumber, None, None, None, None, None, None)  # Create a student object with just the ID
    student.delete()  # Call the delete method

    return redirect('/students')  # Redirect back to the student listing page


@views.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == "POST":
        programCode = request.form.get("courseCode")
        programTitle = request.form.get("courseTitle")
        programCollege = request.form.get("collegeCode")

        # Create a new program instance
        new_program = Programs(programCode, programTitle, programCollege)

        # Save the program to the database
        new_program.save_program()

        # Optionally, redirect or return a success message
        return redirect('/programs')  # Redirect to a page showing programs
    return render_template('programs.html')  # Render the form again if GET request


@views.route('/delete_program/<programCode>', methods=['POST'])
def delete_student(programCode):
    # Find and delete the student by ID number
    program = Programs(programCode, None, None)  # Create a student object with just the ID
    program.delete_program() 

    return redirect('/students')  # Redirect back to the student listing page


@views.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == "POST":
        collegeCode = request.form.get("collegeCode")
        collegeName = request.form.get("collegeName")

        # Create a new college instance
        new_college = Colleges(collegeCode, collegeName)

        # Save the college to the database
        new_college.save_college()

        # Optionally, redirect or return a success message
        return redirect('/colleges')  # Redirect to a page showing colleges
    return render_template('college.html')  # Render the form again if GET request
