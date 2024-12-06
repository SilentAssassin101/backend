from utils import execute_query, addUser
from auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

TEST_PASSWORD = os.getenv("TEST_PASSWORD")


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
    execute_query(
        """CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY,
            ownerId INTEGER NOT NULL,
            name TEXT NOT NULL,
            address TEXT NOT NULL)"""
    )
    execute_query(
        """CREATE TABLE IF NOT EXISTS clubMembers (
            clubId INTEGER NOT NULL,
            memberId INTEGER NOT NULL)"""
    )


def activate_all_testing():
    initialize_tables()
    generate_test_user_master()


def generate_test_user():
    firstName = "john"
    lastName = "doe"
    email = "johndoe@gmail.com"
    password = TEST_PASSWORD
    hashed_password = get_password_hash(password=password)
    addUser(firstName=firstName, lastName=lastName, email=email, password=hashed_password)


def generate_test_user_master():
    if not execute_query(
        """SELECT * FROM users""",
        fetch=True
    ):
        generate_test_user()
