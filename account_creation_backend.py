import dbConn
from flask import Flask, request, jsonify

app = Flask(__name__)

cursor, conn = dbConn.get_connection()
    
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
