from flask import Flask, render_template, request, flash, redirect
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for flashing messages

def get_db_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='campuscollabconnect'
    )
    return connection

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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    search_term = request.args.get('search', '')
    like_pattern = f'%{search_term}%'
    
    query = """
    SELECT title, description FROM posts
    WHERE 
        title LIKE %s OR
        description LIKE %s
    """
    
    cursor.execute(query, (like_pattern, like_pattern))
    job_posts = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('CCCSearch.html', job_posts=job_posts)

@app.route('/dashboard')
def dashboard():
    return render_template('CCCDashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
