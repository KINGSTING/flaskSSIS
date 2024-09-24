import sqlite3
from flask import Blueprint, render_template, request, redirect
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
        program = Programs.find_by_id(get_db_connection(), courseCode)
        status = "Enrolled" if program else "Unenrolled"

        # Create a new student instance
        new_student = Students(idNumber, firstName, lastName, courseCode, year, gender, status)
        new_student.save_student()

        return redirect('/students')  # Redirect to a page showing students

    return render_template('add_student.html')  # Render the form again if GET request


@views.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    # Find and delete the student by ID number
    student = Students(idNumber, None, None, None, None, None, None)
    student.delete_student()
    return redirect('/students')


@views.route('/edit_student/<idNumber>', methods=['GET', 'POST'])
def edit_student(idNumber):
    conn = get_db_connection()

    if request.method == 'POST':
        # Fetch the updated values from the form
        new_idNumber = request.form.get("idNumber")
        new_firstName = request.form.get("firstName")
        new_lastName = request.form.get("lastName")
        new_courseCode = request.form.get("courseCode")
        new_year = request.form.get("year")
        new_gender = request.form.get("gender")

        # Log updated values
        print(f"Updated values: IDNumber={new_idNumber}, FirstName={new_firstName}, LastName={new_lastName}")

        # Fetch the student as an instance of Students
        print(f"ID passed to find_by_id: {idNumber}")
        student = Students.find_by_id(conn, idNumber)

        print(f"Fetched student: {student}")

        if student:
            # Update the student using the instance method
            print("hapit na mo work")
            new_status = student.set_status_based_on_program(conn)
            student.update_student(new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender,
                                   new_status)
            conn.commit()  # Save changes to the database
            print("It was a success")
        else:
            print(f"No student found with ID: {idNumber}")

        conn.close()

        # Redirect back to the student list page after editing
        return redirect('/students')

    # If it's a GET request, fetch the current student details for editing
    student = Students.find_by_id(conn, idNumber)

    if not student:
        # If student not found, redirect to the student list
        print(f"No student found with ID: {idNumber}")
        conn.close()
        return redirect('/students')

    conn.close()

    # Render the edit form with current student details
    return render_template('edit_student.html', student=student)


@views.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == "POST":
        programCode = request.form.get("courseCode")
        programTitle = request.form.get("courseTitle")
        programCollege = request.form.get("collegeCode")

        # Create a new program instance
        new_program = Programs(programCode, programTitle, programCollege)
        new_program.save_program()

        return redirect('/programs')  # Redirect to a page showing programs
    return render_template('programs.html')  # Render the form again if GET request


@views.route('/delete_program/<programCode>', methods=['POST'])
def delete_program(programCode):
    # Find and delete the program by program code
    program = Programs(programCode, None, None)
    program.delete_program()
    return redirect('/programs')  # Redirect to the programs page


@views.route('/edit_program/<originalProgramCode>', methods=['GET', 'POST'])
def edit_program(originalProgramCode):
    conn = get_db_connection()

    if request.method == 'POST':
        new_programCode = request.form.get("courseCode")
        new_programTitle = request.form.get("courseTitle")
        new_collegeCode = request.form.get("collegeCode")

        # Fetch the program as an instance of Programs
        program = Programs.find_by_program(conn, originalProgramCode)

        if program:
            # Update the program using the instance method
            program.update_program(conn, new_programCode, new_programTitle, new_collegeCode)

            conn.commit()  # Commit the changes

        conn.close()

        return redirect('/programs')

    # Fetch the current program details for editing if GET request
    program = Programs.find_by_program(conn, originalProgramCode)
    colleges = Colleges.get_all_colleges(conn)
    conn.close()

    return render_template('edit_program.html', program=program, colleges=colleges)


@views.route('/delete_college/<collegeCode>', methods=['POST'])
def delete_college(collegeCode):
    # Find and delete the college by college code
    college = Colleges(collegeCode, None)
    college.delete_college()
    return redirect('/colleges')  # Redirect to the colleges page


@views.route('/edit_college/<originalCollegeCode>', methods=['POST'])
def edit_college(originalCollegeCode):
    conn = get_db_connection()

    # Get the new data from the form
    new_collegeCode = request.form.get('collegeCode')
    new_collegeName = request.form.get('collegeName')

    # Update the college code and name
    Colleges.update_college(conn, originalCollegeCode, new_collegeCode, new_collegeName)

    conn.commit()
    conn.close()

    # Redirect to the colleges page after updating
    return redirect('/colleges')
