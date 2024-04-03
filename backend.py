from flask import Flask, render_template, request, redirect, url_for, flash, session
from mysql.connector import Error
import dbConn
import key
from flask import jsonify

app = Flask(__name__)
app.secret_key = key.makeKey()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = authenticate_user(email, password)
        
        if user:
            session['user_id'] = user['userID']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")

    return render_template('login.html')

def authenticate_user(email, password):
    try:
        conn, cursor = dbConn.get_connection()

        cursor.execute("SELECT * FROM users WHERE email = %s AND p_word = %s", (email, password))
        user = cursor.fetchone()

        if user:
            user_dict = {
                'userID': user[0],
                'email': user[1],
                'p_word': user[2],
                'firstName': user[3],
                'lastName': user[4]
            }
            return user_dict
        else:
            return None

    except Error as e:
        print("Error while connecting to MySQL", e)
        flash("Error occurred while connecting to the database", "error")
        return None

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

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')

        result = create_user(email, password, first_name, last_name)
        
        if result == "Email already exists":
            return jsonify({'error': 'Email already exists'}), 400
        elif result == "Error occurred":
            return jsonify({'error': 'An error occurred during account creation'}), 500
        else:
            return jsonify({'success': 'Account created successfully'}), 200
    else:
        # For GET requests, render the account creation form
        return render_template('account_creation.html')


@app.route('/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        try:
            user_id = session.get('user_id')
            if user_id is None:
                return redirect(url_for('login'))

            title = request.form['title']
            description = request.form['description']
            task_outline = request.form['task_outline']
            research_requirements = request.form['research_requirements']

            insert_post(user_id, title, description, task_outline, research_requirements)
            return redirect(url_for('dashboard'))

        except Error as e:
            print("An error occurred while creating the project:", e)
            return redirect(url_for('create_project'))

    return render_template('create_project.html', error=None)

def insert_post(user_id, title, description, task_outline, research_requirements):
    try:
        conn, cursor = dbConn.get_connection()

        insert_query = """
        INSERT INTO posts (userID, title, description)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, title, description))
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

def get_user_details(user_id):
    try:
        conn, cursor = dbConn.get_connection()

        cursor.execute("SELECT * FROM users WHERE userID = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            user_dict = {
                'userID': user[0],
                'email': user[1],
                'password': user[2],
                'firstName': user[3],
                'lastName': user[4]
            }
            return user_dict
        else:
            return None

    except Error as e:
        print("Error fetching user details:", e)
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user_details = get_user_details(user_id)
        first_name = user_details.get('firstName')
    else:
        first_name = None
    
    return render_template('CCCDashboard.html', first_name=first_name)

@app.route('/manage_posts')
def manage_posts():
    user_id = session.get('user_id')  # Retrieve the current user's ID from the session
    if not user_id:
        # If no user is logged in, redirect to the login page
        flash("Please log in to view your posts.", "warning")
        return redirect(url_for('login'))

    posts_list = []  # Initialize an empty list to hold the post dictionaries
    try:
        conn, cursor = dbConn.get_connection()
        # Adjust the SQL query to select only posts made by the logged-in user
        cursor.execute("""
            SELECT p.postID, u.firstName, u.lastName, p.title, p.description
            FROM posts p
            JOIN users u ON p.userID = u.userID
            WHERE p.userID = %s
        """, (user_id,))
        posts = cursor.fetchall()
        # Convert each tuple to a dictionary
        for post in posts:
            post_dict = {
                'postID': post[0],
                'username': f"{post[1]} {post[2]}",  # Combine first name and last name
                'title': post[3],
                'description': post[4]
            }
            posts_list.append(post_dict)
    except Exception as e:
        print(f"An error occurred while fetching posts: {e}")
        flash("An error occurred while fetching your posts.", "error")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('mPostSelection.html', posts=posts_list)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'POST':
        # Retrieve updated details from the form submission
        title = request.form['title']
        description = request.form['description']
        task_outline = request.form['task_outline']
        research_requirements = request.form['research_requirements']

        try:
            conn, cursor = dbConn.get_connection()
            # Update post
            cursor.execute("""
                UPDATE posts SET title = %s, description = %s WHERE postID = %s
            """, (title, description, post_id))
            
            # First, delete existing entries
            cursor.execute("DELETE FROM tasks WHERE postID = %s", (post_id,))
            cursor.execute("DELETE FROM researchReqs WHERE postID = %s", (post_id,))
            
            # Insert new tasks and research requirements
            for task in task_outline.split(';'):
                cursor.execute("INSERT INTO tasks (postID, taskDescription) VALUES (%s, %s)", (post_id, task.strip()))
            for requirement in research_requirements.split(';'):
                cursor.execute("INSERT INTO researchReqs (postID, requirementDesc) VALUES (%s, %s)", (post_id, requirement.strip()))
            
            conn.commit()
            flash('Post updated successfully.')
            return redirect(url_for('manage_posts'))
        except Exception as e:
            conn.rollback()  # Roll back in case of error
            flash('An error occurred while updating the post.')
            print(f"An error occurred: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        # Handle GET request by fetching post details to pre-fill the form
        try:
            conn, cursor = dbConn.get_connection()
            cursor.execute("SELECT title, description FROM posts WHERE postID = %s", (post_id,))
            post = cursor.fetchone()
            if post:
                # Fetch tasks and research requirements
                cursor.execute("SELECT taskDescription FROM tasks WHERE postID = %s", (post_id,))
                tasks = '; '.join([task[0] for task in cursor.fetchall()])
                cursor.execute("SELECT requirementDesc FROM researchReqs WHERE postID = %s", (post_id,))
                requirements = '; '.join([req[0] for req in cursor.fetchall()])
                post_details = {
                    'title': post[0],
                    'description': post[1],
                    'tasks': tasks,
                    'requirements': requirements
                }
                return render_template('edit_post.html', post=post_details, post_id=post_id)
        except Exception as e:
            flash('An error occurred while fetching the post details.')
            print(f"An error occurred: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        return redirect(url_for('manage_posts'))



@app.route('/sign_out')
def sign_out():
    return redirect(url_for('login'))

@app.route('/submit_resume', methods=['POST'])
def submit_resume():
    if 'resumeFile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['resumeFile']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Correctly identify the MIME type of the uploaded file
    file_mimetype = file.mimetype

    # Map the MIME type to your ENUM values and validate
    mime_type_to_enum = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        # Add more mappings as necessary
    }

    file_type_enum = mime_type_to_enum.get(file_mimetype, None)
    if file_type_enum is None:
        flash("Unsupported file type. Please upload a PDF or DOCX file.")
        return redirect(request.url)

    user_id = session.get('user_id')
    post_id = request.form.get('postID')  

    # Proceed with saving the resume
    # This time, use file_type_enum instead of content_type for the database insertion
    save_resume_to_database(user_id, post_id, file.read(), file_type_enum)  # file.read() is here as an example; consider efficiency for large files

    flash('Resume uploaded successfully')
    return redirect(url_for('dashboard'))

def save_resume_to_database(user_id, post_id, file_content, file_type_enum):
    try:
        conn, cursor = dbConn.get_connection()
        insert_query = """INSERT INTO resumes (userID, postID, resumeFile, fileType) VALUES (%s, %s, %s, %s)"""
        cursor.execute(insert_query, (user_id, post_id, file_content, file_type_enum))
        conn.commit()
    except Error as e:
        print("An error occurred:", e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



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
