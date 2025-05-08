# db_config.py
# This file will store MySQL database connection details.
# For production, consider using environment variables or a .env file for sensitive information.

DB_CONFIG = {
    "host": "localhost",
    "user": "your_db_user",  # Replace with your MySQL username
    "password": "your_db_password",  # Replace with your MySQL password
    "database": "your_db_name",  # Replace with your database name
    "port": 3306,  # Default MySQL port
}
