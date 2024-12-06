import sqlite3


def execute_query(query, params=(), fetch=False):
    with sqlite3.connect("testing.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit


def initialize_table():
    execute_query(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT UNIQUE
        )
        """)


def addUser(firstName: str, lastName: str, email: str):
    execute_query(
        """INSERT INTO users (
        firstName,
        lastName,
        email
        ) VALUES (?,?,?)""",
        params=(firstName, lastName, email)
    )


def findFromEmail(email: str):
    execute_query(
        """SELECT * FROM users WHERE email=? LIMIT 1""",
        params=(email),
        fetch=True
    )


def removeUser(id: int):
    execute_query(
        """DELETE FROM users WHERE id=? LIMIT 1""",
        params=(id)
    )
