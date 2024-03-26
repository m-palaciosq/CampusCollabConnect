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
    
    # Get filter values from query parameters
    search = request.args.get('search', '')
    task_outline = request.args.get('task_outline', '')
    research_requirements = request.args.get('research_requirements', '')
    collaborators = request.args.get('collaborators', '')
    
    # Construct the base query
    query = "SELECT * FROM JobPosts WHERE Title LIKE %s"
    query_params = [f'%{search}%']
    
    # Add additional filters if they are specified
    if task_outline:
        query += " AND TaskOutline LIKE %s"
        query_params.append(f'%{task_outline}%')
    if research_requirements:
        query += " AND ResearchRequirements LIKE %s"
        query_params.append(f'%{research_requirements}%')
    if collaborators:
        query += " AND Collaborators LIKE %s"
        query_params.append(f'%{collaborators}%')
    
    # Execute the query with the filters
    cursor.execute(query, query_params)
    job_posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('CCCSearch.html', job_posts=job_posts)

if __name__ == '__main__':
    app.run(debug=True)
