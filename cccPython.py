from flask import Flask, render_template, request, flash, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a real secret key

# Using a unified database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',  
        user='root',
        password='',      
        database='campuscollabconnect'
    )
    return connection

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        result = authenticate_user(email, password)
        return result
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('CCCDashboard.html')

@app.route('/manage_posts')
def manage_posts():
    return render_template('mPostSelection.html')

@app.route('/sign_out')
def sign_out():
    return redirect(url_for('login'))

@app.route('/search_posts')
def search_posts():
    return render_template('CCCSearch.html')

@app.route('/search')
def search():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts")  # Adjust the table name and fields as necessary
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('CCCSearch.html', job_posts=job_posts)

@app.route('/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        try:
            # Collect form data
            title = request.form['title']
            description = request.form['description']
            task_outline = request.form['task_outline']
            research_requirements = request.form['research_requirements']
            collaborators = request.form.get('collaborators')  # Use .get for optional fields
            # Insert post into the database
            insert_post(title, description, task_outline, research_requirements, collaborators)
            return redirect(url_for('dashboard'))
        except Error as e:
            print("An error occurred while creating the project:", e)
            return redirect(url_for('create_project'))
    return render_template('create_project.html', error=None)

@app.route('/account_creation', methods=['GET'])
def account_creation_form():
    return render_template('account_creation.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    email = request.form['email']
    password = request.form['password']
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    result = create_user(email, password, first_name, last_name)
    return result

@app.route('/submit_resume', methods=['POST'])
def submit_resume():
    if 'resumeFile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['resumeFile']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        # Here you would normally save the file
        return 'File uploaded successfully'

def insert_post(title, description, task_outline, research_requirements, collaborators=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        insert_query = """
        INSERT INTO posts (title, description, taskOutline, researchRequirements, collaborators)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (title, description, task_outline, research_requirements, collaborators))
        conn.commit()
    except Error as e:
        print("An error occurred:", e)
        conn.rollback()  # Important to rollback if an error occurs
        raise
    finally:
        cursor.close()
        conn.close()

def authenticate_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s AND p_word = %s", (email, password))
        user = cursor.fetchone()
        if user:
            return redirect(url_for('dashboard'))
        else:
            return "Invalid email or password", 401
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Error occurred", 500
    finally:
        cursor.close()
        conn.close()

def create_user(email, password, first_name, last_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Email already exists", 409
        insert_query = """
        INSERT INTO users (email, p_word, firstName, lastName)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (email, password, first_name, last_name))
        conn.commit()
        return redirect(url_for('login'))
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Error occurred", 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
