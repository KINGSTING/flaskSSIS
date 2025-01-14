from flask import Blueprint, render_template, request, redirect, flash, url_for
from website.models import Colleges
from website.__init__ import get_db_connection

cbp = Blueprint("cbp", __name__)


# Colleges page
@cbp.route('/colleges', methods=['GET'])
def college_page():
    conn = get_db_connection()
    colleges = Colleges.get_all_colleges(conn)  # This should query your database and return the college list
    print(colleges)  # For debugging purposes, check the content of colleges
    return render_template('college.html', colleges=colleges)


# Add college
@cbp.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == "POST":
        collegeCode = request.form.get("collegeCode")
        collegeName = request.form.get("collegeName")

        db_connection = get_db_connection()  # Get the DB connection

        # Check if the collegeCode already exists
        if Colleges.check_college_exists(db_connection, collegeCode):
            flash(f"College with code {collegeCode} already exists!", "error")
            return redirect(url_for('cbp.college_page'))

        # Add the new college if it doesn't exist
        new_college = Colleges(collegeCode, collegeName)
        new_college.save_college()  # Pass the connection to the save method
        flash("College added successfully!", "success")
        return redirect(url_for('cbp.college_page'))

    return render_template('college.html')


# Delete college
@cbp.route('/delete_college/<collegeCode>', methods=['POST'])
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
    return redirect(url_for('cbp.college_page'))


# Edit college
@cbp.route('/edit_college/<originalCollegeCode>', methods=['POST'])
def edit_college(originalCollegeCode):
    conn = get_db_connection()

    new_collegeCode = request.form.get('collegeCode')
    new_collegeName = request.form.get('collegeName')

    # Call the update_college method with the connection and the necessary arguments
    Colleges.update_college(conn, new_collegeCode, new_collegeName)

    conn.close()  # Close the connection after operations

    flash("College updated successfully!", "success")
    return redirect(url_for('cbp.college_page'))


# Search college
@cbp.route('/search_college', methods=['GET'])
def search_college():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'collegeCode': 'collegeCode',
        'collegeName': 'collegeName'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('cbp.college_page'))

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
        return redirect(url_for('cbp.college_page'))

    if len(results) == 1:
        return render_template('college.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        return render_template('college.html', colleges=results)  # Multiple results
    else:
        flash("No colleges found.", "warning")
        return redirect(url_for('cbp.college_page'))