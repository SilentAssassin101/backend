from utils import initialize_tables, execute_query, addUser
from auth import get_password_hash


def activate_all_testing():
    print("work in progress")
    initialize_tables()
    generate_test_user_master()


def generate_test_user():
    firstName = "john"
    lastName = "doe"
    email = "johndoe@gmail.com"
    password = "secret"
    hashed_password = get_password_hash(password=password)
    addUser(firstName=firstName, lastName=lastName, email=email, password=hashed_password)


def generate_test_user_master():
    if execute_query(
        """SELECT * FROM users""",
        fetch=True
    ):
        generate_test_user()
