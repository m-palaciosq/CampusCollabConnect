from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
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
    if 'resumeFile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['resumeFile']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        # Ensure the directory exists or create it
        save_path = os.path.join('path/to/save', filename)
        file.save(save_path)
        flash('File uploaded successfully')
        return redirect(url_for('dashboard'))  # Adjust the redirect as needed

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

@app.route('/dashboard')
def dashboard():
    # Assuming 'dashboard.html' is the correct template name.
    return render_template('CCCDashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
