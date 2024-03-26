import mysql.connector

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='./')

# Fake JobPosts Data
fake_job_posts = [
    {
        'PostID': 1,
        'UserID': 1,
        'Title': 'Virtual Reality Research',
        'Description': 'Researching different aspects of VR and its impact on education.',
        'TaskOutline': 'Literature review, experiment design, data analysis',
        'ResearchRequirements': 'Background in psychology or education, experience with statistical software',
        'Collaborators': 'None'
    },
    {
        'PostID': 2,
        'UserID': 2,
        'Title': 'Mobile App Development',
        'Description': 'Developing a mobile app for campus navigation and event management.',
        'TaskOutline': 'UI/UX design, backend development, user testing',
        'ResearchRequirements': 'Proficient in React Native or similar frameworks, experience with databases',
        'Collaborators': '1 designer, 1 backend developer'
    }
]

def get_db_connection():
    connection = mysql.connector.connect(
        host='127.0.0.1',  
        port='3307',       
        user='root',
        password='',      
        database='campuscollabconnect'
    )
    return connection

@app.route('/')
def home():
    # Use the fake data instead of database data for testing
    job_posts = fake_job_posts
    return render_template('CCCSearch.html', job_posts=job_posts)




if __name__ == '__main__':
    app.run(debug=True)
