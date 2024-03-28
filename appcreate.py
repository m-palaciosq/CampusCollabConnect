from flask import Flask, render_template
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',  
        port='3306',       
        user='root',
        password='',      
        database='campuscollabconnect'
    )
    return connection
@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts")
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    print(job_posts)
    return render_template('CCCSearch.html', job_posts=job_posts)

@app.route('/search')
def search():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM posts")  # Adjust the table name and fields as necessary
    job_posts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Ensure job_posts is not empty and contains the correct fields
    print(job_posts)
    
    return render_template('CCCSearch.html', job_posts=job_posts)

@app.route('/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            task_outline = request.form['task_outline']
            research_requirements = request.form['research_requirements']
            collaborators = request.form['collaborators']
            # Debugging statements
            print("Form data received:", title, description, task_outline, research_requirements, collaborators)
            insert_job_post(title, description, task_outline, research_requirements, collaborators)
            
            return redirect(url_for('home'))
        except Exception as e:
            print("An error occurred while inserting the job post:", e)
            return render_template('create_project.html', error=str(e))
    return render_template('create_project.html', error=None)

def insert_job_post(title, description, task_outline, research_requirements, collaborators):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO jobposts (Title, Description, TaskOutline, ResearchRequirements, Collaborators)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (title, description, task_outline, research_requirements, collaborators))
        
        connection.commit()
    except Exception as e:
        print("An error occurred while executing the insert query:", e)
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
