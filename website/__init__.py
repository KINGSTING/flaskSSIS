import mysql.connector
from flask import Flask
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader


def create_app():
    load_dotenv()  # Load environment variables from .env
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Cloudinary configuration
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

    from website.routes.student import sbp
    from website.routes.program import pbp
    from website.routes.college import cbp

    app.register_blueprint(sbp, url_prefix="/")
    app.register_blueprint(pbp, url_prefix="/")
    app.register_blueprint(cbp, url_prefix="/")

    create_database()

    return app


def create_database():
    try:
        # Use environment variables for database configuration
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
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
                ON UPDATE CASCADE
            )
        ''')

        # Create the 'student' table without the foreign key constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student (
                IDNumber VARCHAR(255) PRIMARY KEY,
                firstName VARCHAR(255) NOT NULL,
                lastName VARCHAR(255) NOT NULL,
                CourseCode VARCHAR(255),
                Status VARCHAR(255) NOT NULL,
                Year VARCHAR(255) NOT NULL,
                Gender VARCHAR(255) NOT NULL,
                imageURL VARCHAR(255)
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
        # Use environment variables for database connection
        return mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None
