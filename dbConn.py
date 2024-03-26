import mysql.connector

def get_connection():
    conn = mysql.connector.connect(host="localhost", user="root", password="", database ="campuscollabconnect")
    cursor = conn.cursor()
    return cursor, conn