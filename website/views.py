import sqlite3
from flask import Blueprint, render_template, request, redirect, flash, url_for
from .models import Students, Programs, Colleges
from . import get_db_connection  # Import your connection function

views = Blueprint("views", __name__)


# Home page
@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")


# Students page
@views.route('/students', methods=['GET'])
def view_students():
    students = Students.get_all_students(get_db_connection())
    programs = Programs.get_all_programs(get_db_connection())
    return render_template('student.html', students=students, programs=programs)


# Programs page
@views.route('/programs', methods=['GET'])
def view_programs():
    programs = Programs.get_all_programs(get_db_connection())
    colleges = Colleges.get_all_colleges(get_db_connection())
    return render_template('program.html', programs=programs, colleges=colleges)


# Colleges page
@views.route("/colleges")
def collegePage():
    conn = get_db_connection()
    all_colleges = Colleges.get_all_colleges(conn)
    conn.close()
    return render_template("college.html", colleges=all_colleges)


# Add student
@views.route('/add_student', methods=['GET', 'POST'])
def add_student():
    conn = get_db_connection()  # Initialize the DB connection
    if request.method == "POST":
        # Get form data
        idNumber = request.form.get("idNumber")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        courseCode = request.form.get("courseCode")
        year = request.form.get("year")
        gender = request.form.get("gender")

        # Validate ID format
        if not Students.validate_id_format(idNumber):
            flash("ID Number must be in the format YYYY-NNNN (e.g., 2024-0001)", "error")
            return redirect(url_for('views.view_students'))

        # Validate other input fields
        if not all([idNumber, firstName, lastName, courseCode, year, gender]):
            flash("Please fill out all the fields.", "error")
            return redirect(url_for('views.view_students'))

        try:
            # Check if student ID already exists
            if Students.check_id_exists(conn, idNumber):
                flash(f"Student with ID {idNumber} already exists!", "error")
            else:
                # Add new student
                new_student = Students(idNumber, firstName, lastName, courseCode, year, gender, "Enrolled")
                new_student.save_student()
                flash("Student added successfully!", "success")
                # Check and update status if necessary
                Students.check_and_update_status(conn, idNumber)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('views.view_students'))  # Redirect after POST to prevent re-submission

    return render_template('student.html')  # For GET request


# Delete student
@views.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    conn = get_db_connection()
    student = Students.find_by_id(conn, idNumber)
    if student:
        student.delete_student()
        conn.commit()  # Commit the changes
    conn.close()
    return redirect(url_for('views.view_students'))


# Edit student
@views.route('/edit_student/<idNumber>', methods=['GET', 'POST'])
def edit_student(idNumber):
    conn = get_db_connection()

    if request.method == 'POST':
        # Get updated data from the form
        new_idNumber = request.form.get("idNumber")
        new_firstName = request.form.get("firstName")
        new_lastName = request.form.get("lastName")
        new_courseCode = request.form.get("courseCode")
        new_year = request.form.get("year")
        new_gender = request.form.get("gender")

        # Find the student by the original ID
        student = Students.find_by_id(conn, idNumber)

        if student:
            # Check if the new ID number already exists (and it's not the current student)
            existing_student = Students.find_by_id(conn, new_idNumber)
            if existing_student and existing_student.idNumber != idNumber:
                # If the new ID is already in use by another student, flash an error message
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('edit_student', idNumber=idNumber))  # Reload the edit page

            # Proceed with the update
            new_status = student.check_and_set_status(conn)
            student.update_student(new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender,
                                   new_status)
            conn.commit()
            # Check and update status if necessary
            Students.check_and_update_status(conn, new_idNumber)

            # Flash success message
            flash(f"Student ID {new_idNumber} has been updated successfully!", "success")
            conn.close()
            return redirect(url_for('views.view_students'))  # Redirect to the view page after update
        else:
            # If the student is not found, flash an error
            flash(f"Student with ID {idNumber} not found.", "error")

    # If GET request, load the form with current student data
    student = Students.find_by_id(conn, idNumber)
    conn.close()

    return render_template('edit_student.html', student=student)


# Add program
@views.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == "POST":
        programCode = request.form.get("courseCode")
        programTitle = request.form.get("courseTitle")
        programCollege = request.form.get("collegeCode")

        # Check if the programCode already exists
        if Programs.check_program_exists(get_db_connection(), programCode):
            flash(f"Program with code {programCode} already exists!", "error")
            return redirect(url_for('views.view_programs'))

        # Add the new program if it doesn't exist
        new_program = Programs(programCode, programTitle, programCollege)
        new_program.save_program()
        flash("Program added successfully!", "success")
        return redirect(url_for('views.view_programs'))

    return render_template('program.html')


# Delete program
@views.route('/delete_program/<programCode>', methods=['POST'])
def delete_program(programCode):
    conn = get_db_connection()
    try:
        # Update the status of students to "unenrolled"
        conn.execute("UPDATE student SET Status = 'Unenrolled' WHERE CourseCode = ?", (programCode,))

        # Now delete the program
        conn.execute("DELETE FROM program WHERE programCode = ?", (programCode,))
        conn.commit()
        flash(f"Program with code {programCode} deleted and associated students set to Unenrolled.", "success")
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        flash(f"An error occurred while trying to delete the program: {str(e)}", "error")
    finally:
        conn.close()

    return redirect(url_for('views.programPage'))  # Adjust this to your specific page


# Edit program
@views.route('/edit_program/<originalProgramCode>', methods=['GET', 'POST'])
def edit_program(originalProgramCode):
    conn = get_db_connection()

    if request.method == 'POST':
        new_programCode = request.form.get("courseCode")
        new_programTitle = request.form.get("courseTitle")
        new_collegeCode = request.form.get("collegeCode")

        program = Programs.find_by_program(conn, originalProgramCode)
        if program:
            program.update_program(conn, new_programCode, new_programTitle, new_collegeCode)
            conn.commit()

        conn.close()
        return redirect(url_for('views.view_programs'))

    program = Programs.find_by_program(conn, originalProgramCode)
    colleges = Colleges.get_all_colleges(conn)
    conn.close()

    return render_template('edit_program.html', program=program, colleges=colleges)


@views.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == "POST":
        collegeCode = request.form.get("collegeCode")
        collegeName = request.form.get("collegeName")

        # Check if the collegeCode already exists
        if Colleges.check_college_exists(get_db_connection(), collegeCode):
            flash(f"College with code {collegeCode} already exists!", "error")
            return redirect(url_for('views.collegePage'))  # Make sure the route exists

        # Add the new college if it doesn't exist
        new_college = Colleges(collegeCode, collegeName)
        new_college.save_college()
        flash("College added successfully!", "success")
        return redirect(url_for('views.collegePage'))  # Make sure the route exists

    return render_template('college.html')


# Delete college
@views.route('/delete_college/<collegeCode>', methods=['POST'])
def delete_college(collegeCode):
    conn = get_db_connection()
    college = Colleges.find_by_college(conn, collegeCode)

    if college:
        college.delete_college()  # This should handle the deletion logic
        conn.commit()  # Commit the changes
        flash(f"College with code {collegeCode} deleted successfully.", "success")
    else:
        flash(f"No college found with code {collegeCode}.", "error")

    conn.close()
    return redirect(url_for('views.collegePage'))

# Edit college
@views.route('/edit_college/<originalCollegeCode>', methods=['POST'])
def edit_college(originalCollegeCode):
    conn = get_db_connection()

    new_collegeCode = request.form.get('collegeCode')
    new_collegeName = request.form.get('collegeName')

    Colleges.update_college(conn, originalCollegeCode, new_collegeCode, new_collegeName)
    conn.commit()
    conn.close()

    return redirect(url_for('collegePage'))
