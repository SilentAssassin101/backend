from typing import Union, Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from utils import initialize_tables, getGunsFromUser, getUserFromEmail, addUser
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError

load_dotenv()

SECRET_KEY = os.getenv("PASSLIB_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if SECRET_KEY is None:
    raise ValueError("PASSLIB_KEY environment variable not set!")

initialize_tables()


app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # TODO: Move this logic to its own file


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = get_user_dict_from_email(email=username)
    if not verify_password(password, user.hashed_password):
        return False
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


def get_user_dict_from_email(email: str):
    user_list = getUserFromEmail(email)
    if not user_list:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    user = UserInDB(**map_user_list(user_list))
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_dict_from_email(email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def generateTestUser():
    firstName = "john"
    lastName = "doe"
    email = "johndoe@gmail.com"
    password = "secret"
    hashed_password = get_password_hash(password=password)
    addUser(firstName=firstName, lastName=lastName, email=email, password=hashed_password)


# generateTestUser()


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/{user_id}/guns")
def get_user_guns(user_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    guns = getGunsFromUser(user_id)
    return {"user_id": user_id, "user_guns": guns}


@app.get("/api/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/api/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
