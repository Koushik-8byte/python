from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to start the app: {e}")
