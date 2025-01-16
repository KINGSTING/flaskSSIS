from flask import Blueprint, render_template, request, redirect, flash, url_for
from website.models import Students, Programs
from website.__init__ import get_db_connection
import cloudinary.uploader

sbp = Blueprint("sbp", __name__)


# Home page
@sbp.route("/")
@sbp.route("/home")
def home():
    return render_template("home.html")
# Students page
@sbp.route('/students', methods=['GET'])
def view_students():
    db_connection = get_db_connection()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of students per page
    offset = (page - 1) * per_page

    # Get the list of students with pagination
    students = Students.get_all_students(db_connection, offset, per_page)

    for student in students:
        student_id = student['IDNumber']
        Students.check_and_update_status(db_connection, student_id)

    # Get all programs for the dropdown or selection
    programs = Programs.get_all_programs(db_connection)

    # Get total number of students for pagination controls
    total_students = Students.get_student_count(db_connection)

    # Calculate total number of pages
    total_pages = (total_students // per_page) + (1 if total_students % per_page else 0)

    # Render the template with paginated students, programs, and pagination info
    return render_template('student.html', students=students, programs=programs, page=page, total_pages=total_pages)


# Add student
@sbp.route('/add_student', methods=['GET', 'POST'])
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
        file = request.files.get('file')  # Handle the file upload

        # Validate ID format
        if not Students.validate_id_format(idNumber):
            flash("ID Number must be in the format YYYY-NNNN (e.g., 2024-0001)", "error")
            return redirect(url_for('sbp.view_students'))

        # Validate other input fields
        if not all([idNumber, firstName, lastName, courseCode, year, gender]):
            flash("Please fill out all the fields.", "error")
            return redirect(url_for('sbp.view_students'))

        # Handle image upload
        image_url = None
        if file and file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                flash(f"An error occurred during image upload: {str(e)}", "error")
                return redirect(url_for('sbp.view_students'))

        try:
            # Check if student ID already exists
            if Students.check_id_exists(conn, idNumber):
                flash(f"Student with ID {idNumber} already exists!", "error")
            else:
                # Add new student with image URL
                new_student = Students(idNumber, firstName, lastName, courseCode, year, gender, "Enrolled", image_url=image_url)
                new_student.save_student(conn)  # Pass the connection to the save method
                flash("Student added successfully!", "success")

                # Check and update status if necessary
                Students.check_and_update_status(conn, idNumber)

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('sbp.view_students'))  # Redirect after POST to prevent re-submission

    return render_template('student.html')


# Delete student
@sbp.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    conn = get_db_connection()

    # Use the Students class to find the student
    student = Students.find_by_id(conn, idNumber)

    if student:
        print(f"Student found: {student.firstName} {student.lastName} (ID: {student.idNumber})")
        student.delete_student(conn)  # Proceed with deletion
    else:
        print("Student not found. Cannot delete.")

    conn.close()
    return redirect(url_for('sbp.view_students'))



@sbp.route('/edit_student/<idNumber>', methods=['GET', 'POST'])
def edit_student(idNumber):
    conn = get_db_connection()  # Ensure this is a connection object

    if request.method == 'POST':
        new_idNumber = request.form.get("idNumber")
        new_firstName = request.form.get("firstName")
        new_lastName = request.form.get("lastName")
        new_courseCode = request.form.get("courseCode")
        new_year = request.form.get("year")
        new_gender = request.form.get("gender")

        # Handle file upload
        file = request.files.get('file')
        image_url = None
        if file and file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                flash(f"An error occurred during image upload: {str(e)}", "error")
                return redirect(url_for('sbp.view_students'))

        student = Students.find_by_id(conn, idNumber)

        if student:
            existing_student = Students.find_by_id(conn, new_idNumber)
            if existing_student and existing_student['IDNumber'] != idNumber:
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('sbp.edit_student', idNumber=idNumber))

            # Ensure conn is passed as a connection object to the update function
            if image_url:
                Students.update_student_info(conn,new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, image_url, idNumber)
            else:
                Students.update_student_info(conn,new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, idNumber)

            Students.check_and_update_status(conn, new_idNumber)
            flash(f"Student ID {new_idNumber} has been updated successfully!", "success")
            conn.close()  # Close connection at the end
            return redirect(url_for('sbp.view_students'))
        else:
            flash(f"Student with ID {idNumber} not found.", "error")
            conn.close()
            return redirect(url_for('sbp.view_students'))

    student = Students.find_by_id(conn, idNumber)
    conn.close()

    return render_template('edit_student.html', student=student)



@sbp.route('/search_student', methods=['GET'])
def search_student():
    conn = get_db_connection()
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

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
        flash("Invalid search field!", "danger")
        return redirect(url_for('sbp.view_students'))

    # Perform the search based on the field
    if search_field == 'idNumber':
        # Search for students by ID number (exact match)
        result = Students.search_student_by_id(conn, search_value.strip())
        results = [result] if result else []  # Wrap result in a list if found, else empty list
    elif search_field == 'gender':
        # Search for students by gender with exact matching
        results = Students.search_student_by_gender(conn, search_value.strip())
    else:
        # Search for students using partial match for other fields
        results = Students.search_student_by_field(conn, search_field, search_value.strip())

    # Debugging logs
    print("Search Field:", search_field)
    print("Search Value:", search_value.strip())
    print("Search Results:", results)

    # Handle case if no results were found
    if results:
        return render_template('student.html', students=results)
    else:
        flash("No students found.", "warning")
        return redirect(url_for('sbp.view_students'))

