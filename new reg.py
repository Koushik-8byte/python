from flask import Flask, render_template, request
import mysql.connector
from werkzeug.security import generate_password_hash
from Crypto.Cipher import AES
import base64
import hashlib

app = Flask(__name__)

# 🔐 AES decryption function
def decrypt_password(encrypted_text, secret_key):
    try:
        key = hashlib.sha256(secret_key.encode()).digest()
        encrypted_data = base64.b64decode(encrypted_text)
        iv = encrypted_data[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data[16:])
        return decrypted.rstrip(b"\0").decode('utf-8')
    except Exception as e:
        print("Decryption error:", e)
        return None

# 📝 Registration route
@app.route('/', methods=['GET', 'POST'])
def register_form():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        encrypted_password = request.form['password']

        # Decrypt password
        secret_key = "your-secret-key"  # Must match the key used in CryptoJS
        raw_password = decrypt_password(encrypted_password, secret_key)

        if not raw_password:
            return render_template("register.html", error="Password decryption failed.")

        # Hash password before storing
        password = generate_password_hash(raw_password)

        # Connect to MySQL
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

        # Check for existing user
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()
        if existing_user:
            cur.close()
            mydb.close()
            return render_template("register.html", error="User already exists with this username or email!")

        # Insert new user
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        mydb.commit()
        cur.close()
        mydb.close()
        return render_template("register.html", message="Registration successful!")

    return render_template("register.html")

# 🛠️ Initialize database
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
