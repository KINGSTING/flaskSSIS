import sqlite3
from flask import Flask
from os import path

DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"

    from .views import views
    # from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    # app.register_blueprint(auth, url_prefix="/")

    create_database(app)

    return app


# Create database here
def create_database(app):
    # Check if the database exists, and create tables if not
    if not path.exists("website/" + DB_NAME):
        with app.app_context():  # Ensure application context is available
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Create `student` table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student (
                    IDNumber TEXT PRIMARY KEY,
                    firstName TEXT NOT NULL,
                    lastName TEXT NOT NULL,
                    CourseCode TEXT NOT NULL,
                    Status TEXT NOT NULL,
                    Year TEXT NOT NULL,
                    Gender TEXT NOT NULL,
                    FOREIGN KEY (CourseCode) REFERENCES program(programCode)
                )
            ''')

            # Create `program` table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS program (
                    programCode TEXT PRIMARY KEY,
                    programTitle TEXT,
                    programCollege TEXT,
                    FOREIGN KEY (programCollege) REFERENCES college(collegeCode)
                )
            ''')

            # Create `college` table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS college (
                    collegeCode TEXT PRIMARY KEY,
                    collegeName TEXT
                )
            ''')

            conn.commit()  # Commit the changes
            conn.close()  # Close the connection

        print("Created database and tables!")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enable named column access
    return conn
