from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
import dbConn

app = Flask(__name__)

def create_user(email, password, first_name, last_name):
    try:
        connection, cursor = dbConn.get_connection()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Email already exists"

        sql_query = "INSERT INTO users (email, p_word, firstName, lastName) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (email, password, first_name, last_name))
        connection.commit()

        return "User account created successfully!"

    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Error occurred"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/account_creation', methods=['GET'])
def account_creation_form():
    return render_template('account_creation.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    email = request.form['email']
    password = request.form['password']
    first_name = request.form['firstName']
    last_name = request.form['lastName']

    result = create_user(email, password, first_name, last_name)
    return result

if __name__ == '__main__':
    app.run(debug=True)
