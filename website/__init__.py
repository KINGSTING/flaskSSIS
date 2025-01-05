import mysql.connector
from flask import Flask
import cloudinary
import cloudinary.uploader

DB_NAME = "mydb"  # Name of your MySQL database


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "helloworld"

    # Configure Cloudinary
    cloudinary.config(
        cloud_name='dzn6wdijk',  # Your Cloudinary Cloud Name
        api_key='872366418514214',  # Your Cloudinary API Key
        api_secret='q6DG-UPeMdJllbj3C-ZSmn-33fY'  # Your Cloudinary API Secret
    )

    from .views import views
    # from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    # app.register_blueprint(auth, url_prefix="/")

    create_database(app)

    return app


def create_database(app):
    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Create the 'college' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS college (
                collegeCode VARCHAR(255) PRIMARY KEY,
                collegeName VARCHAR(255) NOT NULL
            )
        ''')

        # Create the 'program' table with both ON DELETE CASCADE and ON UPDATE CASCADE
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS program (
                programCode VARCHAR(255) PRIMARY KEY,
                programTitle VARCHAR(255) NOT NULL,
                programCollege VARCHAR(255),
                FOREIGN KEY (programCollege) REFERENCES college(collegeCode) 
                ON DELETE CASCADE 
                ON UPDATE CASCADE  -- Add ON UPDATE CASCADE here
            )
        ''')

        # Create the 'student' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student (
                IDNumber VARCHAR(255) PRIMARY KEY,
                firstName VARCHAR(255) NOT NULL,
                lastName VARCHAR(255) NOT NULL,
                CourseCode VARCHAR(255),  -- Nullable because of ON DELETE SET NULL
                Status VARCHAR(255) NOT NULL,
                Year VARCHAR(255) NOT NULL,
                Gender VARCHAR(255) NOT NULL,
                imageURL VARCHAR(255),
                FOREIGN KEY (CourseCode) REFERENCES program(programCode) ON DELETE SET NULL
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()

        print("Created database and tables!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="bltr1423",
            database="schooldb"
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
