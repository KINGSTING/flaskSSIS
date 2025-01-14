from flask import Blueprint, render_template, request, redirect, flash, url_for
from website.models import Programs, Colleges
from website.__init__ import get_db_connection


pbp = Blueprint("pbp", __name__)

# Programs page
@pbp.route('/programs', methods=['GET'])
def view_programs():
    db_connection = get_db_connection()
    programs = Programs.get_all_programs(db_connection)
    colleges = Colleges.get_all_colleges(db_connection)
    return render_template('program.html', programs=programs, colleges=colleges)

# Add program
@pbp.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == "POST":
        programCode = request.form.get("courseCode")
        programTitle = request.form.get("courseTitle")
        programCollege = request.form.get("collegeCode")

        # Check if the programCode already exists
        if Programs.check_program_exists(get_db_connection(), programCode):
            flash(f"Program with code {programCode} already exists!", "error")
            return redirect(url_for('pbp.view_programs'))

        # Add the new program if it doesn't exist
        new_program = Programs(programCode, programTitle, programCollege)
        new_program.save_program()  # Pass the connection to the save method
        flash("Program added successfully!", "success")
        return redirect(url_for('pbp.view_programs'))

    return render_template('program.html')


# Delete program
@pbp.route('/delete_program/<program_code>', methods=['POST'])
def delete_program(program_code):
    conn = get_db_connection()
    try:
        Programs.delete_program(conn, program_code)
        flash("Program deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while trying to delete the program: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for('pbp.view_programs'))


# Edit program
@pbp.route('/edit_program/<originalProgramCode>', methods=['GET', 'POST'])
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
        return redirect(url_for('pbp.view_programs'))

    program = Programs.find_by_program(conn, originalProgramCode)
    colleges = Colleges.get_all_colleges(conn)
    conn.close()

    return render_template('edit_program.html', program=program, colleges=colleges)


# Search program
@pbp.route('/search_program', methods=['GET'])
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
        return redirect(url_for('pbp.program_page'))

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
        return redirect(url_for('pbp.program_page'))

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
        return redirect(url_for('pbp.program_page'))