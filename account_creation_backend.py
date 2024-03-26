import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Connect to MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="campuscollabconnect"
)

# Create cursor
cursor = conn.cursor()
    
@app.route('/account_creation_backend', methods=['POST'])
def submit_form():
    # Get form data
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    password = request.form['p_word']

    # Insert into users table
    cursor.execute('''INSERT INTO users (email, p_word, firstName, lastName)
                      VALUES (%s, %s, %s, %s)''', (email, password, firstName, lastName))
    conn.commit()

    return jsonify({'message': 'User registered successfully'})

if __name__ == '__main__':
    app.run(debug=True)
