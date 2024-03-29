from flask import Flask, render_template, request, redirect, url_for, flash
from mysql.connector import Error
import dbConn

app = Flask(__name__)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        result = authenticate_user(email, password)
        
        if result == "success":
            return redirect(url_for('dashboard'))
        else:
            return result

    return render_template('login.html')

# part of login
def authenticate_user(email, password):
    try:
        conn, cursor = dbConn.get_connection()

        cursor.execute("SELECT * FROM users WHERE email = %s AND p_word = %s", (email, password))
        user = cursor.fetchone()

        if user:
            return "success"  # Authentication successful
        else:
            return "Invalid email or password"

    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Error occurred"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_user(email, password, first_name, last_name):
    try:
        conn, cursor = dbConn.get_connection()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Email already exists"

        sql_query = "INSERT INTO users (email, p_word, firstName, lastName) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (email, password, first_name, last_name))
        conn.commit()

        return redirect(url_for('login'))

    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Error occurred"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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

@app.route('/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            task_outline = request.form['task_outline']
            research_requirements = request.form['research_requirements']

            insert_post(title, description, task_outline, research_requirements)
            return redirect(url_for('dashboard'))

        except Error as e:
            print("An error occurred while creating the project:", e)
            return redirect(url_for('create_project'))

    return render_template('create_project.html', error=None)

def insert_post(title, description, task_outline, research_requirements):
    try:
        conn, cursor = dbConn.get_connection()

        insert_query = """
        INSERT INTO posts (title, description)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (title, description))
        post_id = cursor.lastrowid

        insert_query = """
        INSERT INTO tasks (postID, taskDescription)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (post_id, task_outline))

        insert_query = """
        INSERT INTO researchReqs (postID, requirementDesc)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (post_id, research_requirements))

        conn.commit()
        
    except Error as e:
        print("An error occurred while executing the insert query:", e)
        raise

    finally:
        cursor.close()
        conn.close()

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

@app.route('/submit_resume', methods=['POST'])
def submit_resume():
    if 'resumeFile' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    file = request.files['resumeFile']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    if file:
        flash('File uploaded successfully', 'success')
        return redirect(request.url) 


@app.route('/search')
def search():
    search_term = request.args.get('search', '')
    like_pattern = f'%{search_term}%'

    conn, cursor = dbConn.get_connection()

    query = """
    SELECT p.postID, p.title, p.description,
           GROUP_CONCAT(DISTINCT t.taskDescription SEPARATOR '; ') AS tasks,
           GROUP_CONCAT(DISTINCT r.requirementDesc SEPARATOR '; ') AS requirements
    FROM posts AS p
    LEFT JOIN tasks AS t ON p.postID = t.postID
    LEFT JOIN researchReqs AS r ON p.postID = r.postID
    WHERE p.title LIKE %s OR p.description LIKE %s
    GROUP BY p.postID
    ORDER BY p.postID
    """
    cursor.execute(query, (like_pattern, like_pattern))

    job_posts = cursor.fetchall()

    cursor.close()
    conn.close()

    # Transforming the result into a list of dictionaries for easier handling in the template
    job_posts_dicts = [
        {'postID': post[0], 'title': post[1], 'description': post[2], 'tasks': post[3], 'requirements': post[4]}
        for post in job_posts
    ]

    return render_template('CCCSearch.html', job_posts=job_posts_dicts)

if __name__ == '__main__':
    app.run(debug=True)
