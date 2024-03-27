import mysql.connector

def get_connection():
    conn = mysql.connector.connect(host="localhost", user="root", port = "3306", password="", database ="campuscollabconnect")
    cursor = conn.cursor()
    return conn, cursor