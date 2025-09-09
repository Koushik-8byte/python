from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'mysecretkey'

@app.route('/', methods=['GET', 'POST'])  # Default route shows login
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
#- The password is hashed using SHA-256 before submission in the clint side .

        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='root',
                database='usersdata'
            )
            cur = mydb.cursor()
            cur.execute("SELECT password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            mydb.close()

            if user and check_password_hash(user[0], password):
                return "Welcome!"
            else:
                flash("❌ Invalid email or password.")
                return redirect(url_for("login"))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])  # Registration form moved here
def register_form():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("❌ Passwords do not match.")
            return redirect(url_for("register_form"))

        hashed_password = generate_password_hash(password)

        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='root',
                database='usersdata'
            )
            cur = mydb.cursor()

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
                flash("⚠️ User already exists.")
                cur.close()
                mydb.close()
                return redirect(url_for("register_form"))

            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password))
            mydb.commit()
            cur.close()
            mydb.close()

            flash("✅ Registration successful! Please log in.")
            return redirect(url_for("login"))

        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            return redirect(url_for("register_form"))

    return render_template("register.html")

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
