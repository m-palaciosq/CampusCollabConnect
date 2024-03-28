from flask import Flask, render_template, request, flash, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  
        database='campuscollabconnect'  
    )
    return connection

@app.route('/submit_resume', methods=['POST'])
def submit_resume():
    # Check if the post request has the file part
    if 'resumeFile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['resumeFile']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        # Save the file to a secure location, process as needed
        # For example: file.save(os.path.join('/path/to/save', file.filename))
        return 'File uploaded successfully' 

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    search_term = request.args.get('search', '')
    query = """
    SELECT title, description FROM posts
    WHERE title LIKE %s OR
          description LIKE %s
    """
    like_pattern = f'%{search_term}%'
    cursor.execute(query, (like_pattern, like_pattern))
    
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('CCCSearch.html', job_posts=job_posts)

if __name__ == '__main__':
    app.run(debug=True)
