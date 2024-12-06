import sqlite3
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Union


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class User(BaseModel):
    id: int
    firstName: str
    lastName: str
    username: str  # email


class UserInDB(User):
    hashed_password: str
    disabled: bool


def execute_query(query, params=(), fetch=False):
    with sqlite3.connect("testing.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()


def initialize_tables():
    print("Initializing Tables")
    execute_query(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT UNIQUE,
            password TEXT,
            disabled int DEFAULT 0
        )
        """)
    execute_query(
        """CREATE TABLE IF NOT EXISTS guns (
            id INTEGER PRIMARY KEY,
            ownerId INTEGER NOT NULL,
            name TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            type TEXT NOT NULL,
            joules REAL NOT NULL
        )
        """)


def addUser(firstName: str, lastName: str, email: str, password: str):
    execute_query(
        """INSERT INTO users (
        firstName,
        lastName,
        email,
        password,
        disabled
        ) VALUES (?,?,?,?,?)""",
        params=(firstName, lastName, email, password, False)
    )


def getUserFromEmail(email: str):
    return execute_query(
        """SELECT * FROM users WHERE email=? LIMIT 1""",
        params=(email,),
        fetch=True
    )


def removeUser(id: int):
    execute_query(
        """DELETE FROM users WHERE id=? LIMIT 1""",
        params=(id)
    )


def get_user_dict_from_email(email: str):
    user_list = getUserFromEmail(email)
    if not user_list:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    user = UserInDB(**map_user_list(user_list))
    return user


def map_user_list(user_list: list):
    # The SQLite database query returns a tuple containing a list
    # We want that list to be a dictionary
    if user_list[0][5] == 0:
        disabled = False
    else:
        disabled = True
    user_list_mapped = {
        'id': user_list[0][0],
        'firstName': user_list[0][1],
        'lastName': user_list[0][2],
        'username': user_list[0][3],
        'hashed_password': user_list[0][4],
        'disabled': disabled
    }
    return user_list_mapped
