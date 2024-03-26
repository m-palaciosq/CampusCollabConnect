from flask import Flask, render_template, request
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

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    search = request.args.get('search', default='%')
    task_outline = request.args.get('taskOutline', default='%')  # Adjusted to taskOutline
    research_requirements = request.args.get('researchRequirements', default='%')  # Adjusted to researchRequirements
    collaborators = request.args.get('collaborators', default='%')
    
    query = """
    SELECT * FROM posts
    WHERE 
        title LIKE %s AND
        taskOutline LIKE %s AND 
        researchRequirements LIKE %s AND 
        collaborators LIKE %s
    """
    cursor.execute(query, (search, task_outline, research_requirements, collaborators))
    
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('CCCSearch.html', job_posts=job_posts)

if __name__ == '__main__':
    app.run(debug=True)
