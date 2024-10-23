import mysql.connector  # Import MySQL Connector
from flask import Blueprint, render_template, request, redirect, flash, url_for
from .models import Students, Programs, Colleges
from . import get_db_connection  # Import your connection function
import cloudinary.uploader

views = Blueprint("views", __name__)


# Home page
@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")


# Students page
@views.route('/students', methods=['GET'])
def view_students():
    db_connection = get_db_connection()
    students = Students.get_all_students(db_connection)

    for student in students:
        student_id = student['IDNumber']
        Students.check_and_update_status(db_connection, student_id)

    programs = Programs.get_all_programs(db_connection)
    return render_template('student.html', students=students, programs=programs)


# Programs page
@views.route('/programs', methods=['GET'])
def view_programs():
    db_connection = get_db_connection()
    programs = Programs.get_all_programs(db_connection)
    colleges = Colleges.get_all_colleges(db_connection)
    return render_template('program.html', programs=programs, colleges=colleges)


# Colleges page
@views.route('/colleges', methods=['GET'])
def college_page():
    conn = get_db_connection()
    colleges = Colleges.get_all_colleges(conn)  # This should query your database and return the college list
    print(colleges)  # For debugging purposes, check the content of colleges
    return render_template('college.html', colleges=colleges)


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
                new_student.save_student()  # Pass the connection to the save method
                flash("Student added successfully!", "success")
                # Check and update status if necessary
                Students.check_and_update_status(conn, idNumber)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('views.view_students'))  # Redirect after POST to prevent re-submission

    return render_template('student.html')  # For GET request


# Delete student
# Delete student
@views.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    conn = get_db_connection()
    cursor = conn.cursor()  # Create a cursor object
    student = Students.find_by_id(conn, idNumber)
    if student:
        student.delete_student(conn)  # Make sure this method uses the cursor if needed
        conn.commit()  # Commit the changes
    cursor.close()  # Close the cursor
    conn.close()  # Close the connection
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
            if existing_student and existing_student['IDNumber'] != idNumber:
                # If the new ID is already in use by another student, flash an error message
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('views.edit_student', idNumber=idNumber))  # Reload the edit page

            # Proceed with the update using SQL
            cursor = conn.cursor()  # Create a cursor object
            cursor.execute("""UPDATE student 
                              SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s 
                              WHERE IDNumber = %s""",
                           (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, idNumber))
            conn.commit()
            cursor.close()  # Close the cursor

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
        new_program.save_program()  # Pass the connection to the save method
        flash("Program added successfully!", "success")
        return redirect(url_for('views.view_programs'))

    return render_template('program.html')


# Delete program
@views.route('/delete_program/<program_code>', methods=['POST'])
def delete_program(program_code):
    conn = get_db_connection()
    try:
        Programs.delete_program(conn, program_code)
        flash("Program deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while trying to delete the program: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('views.view_programs'))


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


# Add college
@views.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == "POST":
        collegeCode = request.form.get("collegeCode")
        collegeName = request.form.get("collegeName")

        db_connection = get_db_connection()  # Get the DB connection

        # Check if the collegeCode already exists
        if Colleges.check_college_exists(db_connection, collegeCode):
            flash(f"College with code {collegeCode} already exists!", "error")
            return redirect(url_for('views.college_page'))

        # Add the new college if it doesn't exist
        new_college = Colleges(collegeCode, collegeName)
        new_college.save_college()  # Pass the connection to the save method
        flash("College added successfully!", "success")
        return redirect(url_for('views.college_page'))

    return render_template('college.html')


# Delete college
@views.route('/delete_college/<collegeCode>', methods=['POST'])
def delete_college(collegeCode):
    conn = get_db_connection()
    college = Colleges.find_by_college(conn, collegeCode)

    if college:
        college.delete_college()  # Pass the connection to the delete method
        conn.commit()  # Commit the changes
        flash(f"College with code {collegeCode} deleted successfully.", "success")
    else:
        flash(f"No college found with code {collegeCode}.", "error")

    conn.close()
    return redirect(url_for('views.college_page'))


# Edit college
@views.route('/edit_college/<originalCollegeCode>', methods=['POST'])
def edit_college(originalCollegeCode):
    conn = get_db_connection()

    new_collegeCode = request.form.get('collegeCode')
    new_collegeName = request.form.get('collegeName')

    # Call the update_college method with the connection and the necessary arguments
    Colleges.update_college(conn, new_collegeCode, new_collegeName)

    conn.close()  # Close the connection after operations

    flash("College updated successfully!", "success")
    return redirect(url_for('views.college_page'))


# Search college
@views.route('/search_college', methods=['GET'])
def search_college():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'collegeCode': 'collegeCode',
        'collegeName': 'collegeName'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('views.college_page'))

    query = f"SELECT * FROM college WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
    params = [f"%{search_value}%"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Enable dictionary cursor
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        flash("An error occurred while searching: " + str(e), "danger")
        return redirect(url_for('views.college_page'))

    if len(results) == 1:
        return render_template('college.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        return render_template('college.html', colleges=results)  # Multiple results
    else:
        flash("No colleges found.", "warning")
        return redirect(url_for('views.college_page'))


# Search program
@views.route('/search_program', methods=['GET'])
def search_program():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    # Define a mapping of allowed search fields to actual database columns
    field_map = {
        'programCode': 'programCode',
        'programTitle': 'programTitle',
        'programCollege': 'programCollege'
    }

    # If the search field is invalid, flash an error and redirect
    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('views.program_page'))

    # Build the SQL query dynamically based on the search field
    query = f"SELECT * FROM program WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
    params = [f"%{search_value}%"]  # Use wildcard search

    try:
        # Establish a connection to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Enable dictionary cursor for named columns
        cursor.execute(query, params)  # Execute the query with the search value
        results = cursor.fetchall()  # Fetch all matching results
        cursor.close()
        conn.close()
    except Exception as e:
        # Handle any errors that may occur during the database operation
        flash("An error occurred while searching: " + str(e), "danger")
        return redirect(url_for('views.program_page'))

    # Check the number of results and render the appropriate template
    if len(results) == 1:
        # If exactly one result is found, render the page with that result
        return render_template('program.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        # If multiple results are found, render the page with a list of programs
        return render_template('program.html', programs=results)  # Multiple results
    else:
        # If no results are found, flash a warning and redirect
        flash("No programs found.", "warning")
        return redirect(url_for('views.program_page'))


@views.route('/search_student', methods=['GET'])
def search_student():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    # Define a mapping of allowed search fields to actual database columns
    field_map = {
        'idNumber': 'IDNumber',
        'firstName': 'firstName',
        'lastName': 'lastName',
        'course': 'CourseCode',
        'yearLevel': 'Year',
        'gender': 'Gender',
        'status': 'Status'
    }

    # If the search field is invalid, flash an error and redirect
    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('views.view_students'))

    # Determine whether to use LIKE or = based on the search field
    if search_field == 'gender':
        # Use exact match for gender
        query = f"SELECT * FROM student WHERE {field_map[search_field]} = %s"
    else:
        # Use wildcard search for other fields
        query = f"SELECT * FROM student WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"

    params = [search_value] if search_field == 'gender' else [f"%{search_value}%"]  # No wildcards for gender

    try:
        # Establish a connection to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Enable dictionary cursor for named columns
        cursor.execute(query, params)  # Execute the query with the search value
        results = cursor.fetchall()  # Fetch all matching results
        cursor.close()
        conn.close()
    except Exception as e:
        # Handle any errors that may occur during the database operation
        flash("An error occurred while searching: " + str(e), "danger")
        return redirect(url_for('views.view_students'))

    # Check the number of results and render the appropriate template
    if len(results) == 1:
        # If exactly one result is found, render the page with that result
        return render_template('student.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        # If multiple results are found, render the page with a list of students
        return render_template('student.html', students=results)  # Multiple results
    else:
        # If no results are found, flash a warning and redirect
        flash("No students found.", "warning")
        return redirect(url_for('views.view_students'))


# Upload image
@views.route('/upload_image', methods=['POST'])
def upload_image():
    # Check if a file was submitted
    if 'file' not in request.files:
        flash("No file part", "error")
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash("No selected file", "error")
        return redirect(request.url)

    if file:
        try:
            # Upload the image to Cloudinary
            result = cloudinary.uploader.upload(file)

            # Store the uploaded image URL in the database or wherever needed
            image_url = result['secure_url']
            flash("Image uploaded successfully!", "success")

            # Optionally, redirect or render a page showing the uploaded image
            return render_template('student.html', image_url=image_url)

        except Exception as e:
            flash(f"An error occurred during image upload: {str(e)}", "error")
            return redirect(request.url)
