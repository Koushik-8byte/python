from flask import Flask, render_template, request
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Route to show the registration form
@app.route('/', methods=['GET', 'POST'])
def register_form():
    if request.method == 'POST':
        # Fetch data from the form
        username = request.form['username']
        email = request.form['email']
        raw_password = request.form['password']
        password = generate_password_hash(raw_password)


        # Connect to MySQL and insert data
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='root',
            database='usersdata'
        )
        cur = mydb.cursor()

        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                email VARCHAR(100),
                password VARCHAR(255)
            )
        """)
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            mydb.close()
            return "User already exists with this username or email!"

        # Insert form data
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        mydb.commit()
        cur.close()
        mydb.close()

        return "Registration successful!"

    return render_template("register.html")

# Create database if not exists
def init_db():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='root'
    )
    cur = mydb.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS usersdata")
    mydb.commit()
    cur.close()
    mydb.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
