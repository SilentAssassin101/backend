from utils import initialize_tables, execute_query, addUser
from auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

TEST_PASSWORD = os.getenv("TEST_PASSWORD")


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
