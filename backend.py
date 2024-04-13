from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, flash, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
import io
from mysql.connector import Error
import dbConn
import key
from datetime import datetime

app = Flask(__name__)
app.secret_key = key.makeKey()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 


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

@app.route('/account_creation')
def account_creation_form():
    return render_template('account_creation.html')

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
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your posts.", "warning")
        return redirect(url_for('login'))

    posts_list = [] 
    try:
        conn, cursor = dbConn.get_connection()
        cursor.execute("""
            SELECT p.postID, u.firstName, u.lastName, p.title, p.description
            FROM posts p
            JOIN users u ON p.userID = u.userID
            WHERE p.userID = %s
        """, (user_id,))
        posts = cursor.fetchall()
        for post in posts:
            post_dict = {
                'postID': post[0],
                'username': f"{post[1]} {post[2]}",
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


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to log in to delete posts.", "error")
        return redirect(url_for('login'))

    try:
        conn, cursor = dbConn.get_connection()

        # First, check if the current user is the owner of the post
        cursor.execute("SELECT userID FROM posts WHERE postID = %s", (post_id,))
        result = cursor.fetchone()
        if not result or result[0] != user_id:
            flash("You are not authorized to delete this post.", "error")
            return redirect(url_for('manage_posts'))
        
        # Delete related entries first due to foreign key constraints.
        cursor.execute("DELETE FROM tasks WHERE postID = %s", (post_id,))
        cursor.execute("DELETE FROM researchReqs WHERE postID = %s", (post_id,))
        cursor.execute("DELETE FROM resumes WHERE postID = %s", (post_id,))
        
        # Now, delete the post itself.
        cursor.execute("DELETE FROM posts WHERE postID = %s", (post_id,))
        conn.commit()
        flash("Post deleted successfully.", "success")
        
    except Error as e:
        conn.rollback()
        flash("An error occurred while deleting the post.", "error")
        print(f"An error occurred: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('manage_posts'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        flash('You must be logged in to send messages.')
        return redirect(url_for('login'))

    receiver_id = request.form.get('receiver_id')
    subject = request.form.get('subject')
    content = request.form.get('content')

    if not receiver_id or not subject or not content:
        flash('All fields are required.')
        return redirect(request.referrer)

    try:
        conn, cursor = dbConn.get_connection()
        query = "INSERT INTO messages (sender_id, receiver_id, subject, content) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (session['user_id'], receiver_id, subject, content))
        conn.commit()
        flash('Message sent successfully.')
    except Error as e:
        flash('An error occurred while sending the message.')
        print(e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('inbox'))

@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        flash('You must be logged in to view your inbox.')
        return redirect(url_for('login'))

    try:
        conn, cursor = dbConn.get_connection()
        query = "SELECT * FROM messages WHERE receiver_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (session['user_id'],))
        messages = cursor.fetchall()
    except Error as e:
        flash('An error occurred while fetching messages.')
        print(e)
        messages = []
    finally:
        cursor.close()
        conn.close()

    return render_template('inbox.html', messages=messages)

@app.route('/message/<int:message_id>')
def read_message(message_id):
    if 'user_id' not in session:
        flash('You must be logged in to read messages.')
        return redirect(url_for('login'))

    try:
        conn, cursor = dbConn.get_connection()
        # Fetch the message
        cursor.execute("SELECT * FROM messages WHERE id = %s AND receiver_id = %s", (message_id, session['user_id']))
        message = cursor.fetchone()

        if message:
            # Mark the message as read if necessary
            if not message['is_read']:
                cursor.execute("UPDATE messages SET is_read = TRUE WHERE id = %s", (message_id,))
                conn.commit()

        else:
            flash('Message not found or you do not have permission to view it.')
            return redirect(url_for('inbox'))
    except Error as e:
        flash('An error occurred while fetching the message.')
        print(e)
    finally:
        cursor.close()
        conn.close()

    return render_template('read_message.html', message=message)

@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if 'user_id' not in session:
        flash('You must be logged in to delete messages.')
        return redirect(url_for('login'))

    try:
        conn, cursor = dbConn.get_connection()
        # Check if the user is the owner of the message
        cursor.execute("SELECT receiver_id FROM messages WHERE id = %s", (message_id,))
        result = cursor.fetchone()

        if result and result['receiver_id'] == session['user_id']:
            cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
            conn.commit()
            flash('Message deleted successfully.')
        else:
            flash('You do not have permission to delete this message.')
    except Error as e:
        flash('An error occurred while deleting the message.')
        print(e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('inbox'))



@app.route('/view_resumes/<int:postID>')
def view_resumes(postID):
    if 'user_id' not in session:
        flash('Please log in to view resumes.', 'info')
        return redirect(url_for('login'))

    post_title = None
    resumes = []
    try:
        conn, cursor = dbConn.get_connection()
        # Fetch the post title
        cursor.execute("SELECT title FROM posts WHERE postID = %s", (postID,))
        post_title_row = cursor.fetchone()
        post_title = post_title_row[0] if post_title_row else "Unknown Post"

        # Fetch resumes as before
        cursor.execute("""
            SELECT r.resumeID, r.userID, r.fileType, u.firstName, u.lastName
            FROM resumes r
            JOIN users u ON r.userID = u.userID
            WHERE r.postID = %s
        """, (postID,))
        resumes = [{
            'resumeID': row[0], 
            'userID': row[1], 
            'fileType': row[2], 
            'firstName': row[3], 
            'lastName': row[4]
        } for row in cursor.fetchall()]
    except Exception as e:
        flash("An error occurred while fetching resumes.", "error")
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('view_resumes.html', postID=postID, postTitle=post_title, resumes=resumes)


@app.route('/download_resume/<int:resumeID>')
def download_resume(resumeID):
    if 'user_id' not in session:
        flash('Please log in to download resumes.', 'info')
        return redirect(url_for('login'))
    
    try:
        conn, cursor = dbConn.get_connection()
        cursor.execute("""
            SELECT r.resumeFile, r.fileType, u.firstName, u.lastName 
            FROM resumes r
            JOIN users u ON r.userID = u.userID
            WHERE r.resumeID = %s
        """, (resumeID,))
        resume = cursor.fetchone()
        if resume:
            resume_file, file_type, first_name, last_name = resume
            safe_first_name = "".join(x for x in first_name if x.isalnum())
            safe_last_name = "".join(x for x in last_name if x.isalnum())
            filename = f"{safe_first_name}_{safe_last_name}_Resume.{file_type}"
            
            return send_file(
                io.BytesIO(resume_file),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash("Resume not found.", "error")
            return redirect(url_for('view_resumes', postID=session.get('current_postID', 0)))
    except Exception as e:
        flash("An error occurred while downloading the resume.", "error")
        print(f"An error occurred: {e}")
        return redirect(url_for('view_resumes', postID=session.get('current_postID', 0)))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task_outline = request.form['task_outline']
        research_requirements = request.form['research_requirements']

        try:
            conn, cursor = dbConn.get_connection()
            cursor.execute("""
                UPDATE posts SET title = %s, description = %s WHERE postID = %s
            """, (title, description, post_id))
            
            cursor.execute("DELETE FROM tasks WHERE postID = %s", (post_id,))
            cursor.execute("DELETE FROM researchReqs WHERE postID = %s", (post_id,))
            
            for task in task_outline.split(';'):
                cursor.execute("INSERT INTO tasks (postID, taskDescription) VALUES (%s, %s)", (post_id, task.strip()))
            for requirement in research_requirements.split(';'):
                cursor.execute("INSERT INTO researchReqs (postID, requirementDesc) VALUES (%s, %s)", (post_id, requirement.strip()))
            
            conn.commit()
            flash('Post updated successfully.')
            return redirect(url_for('manage_posts'))
        except Exception as e:
            conn.rollback()
            flash('An error occurred while updating the post.')
            print(f"An error occurred: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        try:
            conn, cursor = dbConn.get_connection()
            cursor.execute("SELECT title, description FROM posts WHERE postID = %s", (post_id,))
            post = cursor.fetchone()
            if post:
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
    SELECT p.postID, p.title, p.description, p.created_at,
           GROUP_CONCAT(DISTINCT t.taskDescription SEPARATOR '; ') AS tasks,
           GROUP_CONCAT(DISTINCT r.requirementDesc SEPARATOR '; ') AS requirements
    FROM posts AS p
    LEFT JOIN tasks AS t ON p.postID = t.postID
    LEFT JOIN researchReqs AS r ON p.postID = r.postID
    WHERE p.title LIKE %s OR p.description LIKE %s
    GROUP BY p.postID, p.title, p.description, p.created_at
    ORDER BY p.created_at DESC
    """
    cursor.execute(query, (like_pattern, like_pattern))

    job_posts = [
        {
            'postID': post[0], 
            'title': post[1], 
            'description': post[2], 
            'created_at': post[3],
            'tasks': post[4], 
            'requirements': post[5]
        }
        for post in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return render_template('CCCSearch.html', job_posts=job_posts)


@app.errorhandler(RequestEntityTooLarge)
def handle_large_file_error(e):
    flash('File too large. Please upload a file smaller than 16MB.')
    return redirect(request.url), 413

if __name__ == '__main__':
    app.run(debug=True)