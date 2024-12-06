from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from utils import initialize_tables, getGunsFromUser

initialize_tables()

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
