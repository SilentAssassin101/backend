from typing import Union, Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from utils import initialize_tables, getGunsFromUser, getUserFromEmail

initialize_tables()
# from utils import generateTestUser
# generateTestUser()

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


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


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = getUserFromEmail(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    print("user_dict", user_dict)
    user_dict_mapped = {
        'id': user_dict[0][0],
        'firstName': user_dict[0][1],
        'lastName': user_dict[0][2],
        'username': user_dict[0][3],
        'hashed_password': user_dict[0][4]
    }
    user = UserInDB(**user_dict_mapped)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.get("/api/{user_id}/guns")
def get_user_guns(user_id: int):
    guns = getGunsFromUser(user_id)
    return {"user_id": user_id, "user_guns": guns}
