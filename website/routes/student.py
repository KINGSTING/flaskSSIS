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
    cursor = db_connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM student')
    total_students = cursor.fetchone()[0]
    cursor.close()

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
    cursor = conn.cursor()  # Create a cursor object
    student = Students.find_by_id(conn, idNumber)
    if student:
        student.delete_student(conn)  # Make sure this method uses the cursor if needed
        conn.commit()  # Commit the changes
    cursor.close()  # Close the cursor
    conn.close()  # Close the connection
    return redirect(url_for('sbp.view_students'))


# Edit student
@sbp.route('/edit_student/<idNumber>', methods=['GET', 'POST'])
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

        # Handle file upload (to Cloudinary)
        file = request.files.get('file')
        image_url = None  # Default value if no image is uploaded

        if file and file.filename != '':
            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('secure_url')  # Get the secure URL from Cloudinary
            except Exception as e:
                flash(f"An error occurred during image upload: {str(e)}", "error")
                return redirect(url_for('sbp.view_students'))  # Redirect on error

        # Find the student by the original ID
        student = Students.find_by_id(conn, idNumber)

        if student:
            # Check if the new ID number already exists (and it's not the current student)
            existing_student = Students.find_by_id(conn, new_idNumber)
            if existing_student and existing_student['IDNumber'] != idNumber:
                # If the new ID is already in use by another student, flash an error message
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('sbp.edit_student', idNumber=idNumber))  # Reload the edit page

            # Proceed with the update using SQL
            cursor = conn.cursor()  # Create a cursor object
            if image_url:  # Update the image URL if a new image was uploaded
                cursor.execute("""UPDATE student 
                                  SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, imageURL = %s 
                                  WHERE IDNumber = %s""",
                               (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, image_url, idNumber))
            else:
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
            return redirect(url_for('sbp.view_students'))  # Redirect to the view page after update
        else:
            # If the student is not found, flash an error
            flash(f"Student with ID {idNumber} not found.", "error")

    # If GET request, load the form with current student data
    student = Students.find_by_id(conn, idNumber)
    conn.close()

    return render_template('edit_student.html', student=student)


@sbp.route('/search_student', methods=['GET'])
def search_student():
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

    # Adjust the query for the specific field
    if search_field == 'idNumber':
        # Use exact match for idNumber
        query = f"SELECT * FROM student WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
        params = [search_value.strip()]  # Trim input value to avoid mismatches
    elif search_field == 'gender':
        # Gender-specific query for length and exact match
        query = f"""
            SELECT * FROM student 
            WHERE LENGTH({field_map[search_field]}) = LENGTH(TRIM(%s)) 
            AND LOWER({field_map[search_field]}) = LOWER(TRIM(%s))
        """
        params = [search_value.strip(), search_value.strip()]
    else:
        # Use partial match for other fields
        query = f"SELECT * FROM student WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
        params = [f"%{search_value.strip()}%"]

    # Debugging logs
    print("Search Field:", search_field)
    print("Search Value:", search_value.strip())
    print("Executing Query:", query)
    print("With Parameters:", params)

    try:
        # Execute the query
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Use a dictionary cursor
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

    except Exception as e:
        # Handle database errors gracefully
        flash("An error occurred while searching: " + str(e), "danger")
        return redirect(url_for('sbp.view_students'))

    # Render results based on the number of matches
    if results:  # Check if there are any results
        return render_template('student.html', students=results)
    else:
        flash("No students found.", "warning")
        return redirect(url_for('sbp.view_students'))

