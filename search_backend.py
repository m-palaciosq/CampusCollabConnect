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
    
    # Retrieve the unified search term from the query parameters
    search_term = request.args.get('search', '')
    
    # Modify the SQL query to search across multiple fields
    query = """
    SELECT * FROM posts
    WHERE 
        title LIKE %s OR
        taskOutline LIKE %s OR
        researchRequirements LIKE %s OR
        collaborators LIKE %s
    """
    
    like_pattern = f'%{search_term}%'
    cursor.execute(query, (like_pattern, like_pattern, like_pattern, like_pattern))
    
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('CCCSearch.html', job_posts=job_posts)

if __name__ == '__main__':
    app.run(debug=True)
