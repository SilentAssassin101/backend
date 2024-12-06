import sqlite3


def execute_query(query, params=(), fetch=False):
    with sqlite3.connect("testing.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit


def initialize_tables():
    execute_query(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT UNIQUE
        )
        """)
    execute_query(
        """CREATE TABLE IF NOT EXISTS guns (
            id INTEGER PRIMARY KEY,
            ownerId INTEGER NOT NULL,
            name TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            type TEXT NOT NULL
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


def getUserFromEmail(email: str):
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


def addGun(ownerId: int, name: str, manufacturer: str, type: str):
    execute_query(
        """INSERT INTO guns (
        ownerId,
        name,
        manufacturer,
        type
        ) VALUES (?,?,?,?)""",
        params=(ownerId, name, manufacturer, type)
    )


def removeGun(gunId: int):
    execute_query(
        """DELETE FROM guns WHERE id=? LIMIT 1""",
        params=(gunId)
    )


def getGunsFromUser(id: int):
    execute_query(
        """SELECT * FROM guns WHERE ownerId=?""",
        params=(id),
        fetch=True
    )
