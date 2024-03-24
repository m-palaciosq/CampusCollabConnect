import mysql.connector

# Replace 'your_database_name' with the name of your database
# For 'root' user, by default, there might be no password in XAMPP
config = {
    'user': 'root',
    'password': '',  # or your root password if you've set one
    'host': 'localhost',
    'database': 'campuscollabconnect',
    'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # Example query
    cursor.execute("SELECT * FROM posts")

    for row in cursor.fetchall():
        print(row)

    cursor.close()
    cnx.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")

