from utils import execute_query
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from auth import oauth2_scheme, get_current_user


def add_gun(ownerId: int, name: str, manufacturer: str, type: str):
    execute_query(
        """INSERT INTO guns (
        ownerId,
        name,
        manufacturer,
        type
        ) VALUES (?,?,?,?)""",
        params=(ownerId, name, manufacturer, type)
    )


def remove_gun(gun_id: int):
    execute_query(
        """DELETE FROM guns WHERE id=? LIMIT 1""",
        params=(gun_id)
    )


def get_guns_from_user(id: int):
    return execute_query(
        """SELECT * FROM guns WHERE ownerId=?""",
        params=(id),
        fetch=True
    )


def get_gun_owner(gun_id: int):
    return execute_query(
        """SELECT owner FROM guns WHERE id=?""",
        params=(gun_id),
        fetch=True
    )[0]


router = APIRouter()


@router.get("/{user_id}")
def get_user_guns(user_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    guns = get_guns_from_user(user_id)
    return {"user_id": user_id, "user_guns": guns}


@router.get("/me")
def get_my_guns(token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = get_current_user().id
    guns = get_guns_from_user(user_id)
    return {"user_id": user_id, "user_guns": guns}


@router.post("/add")  # TODO: image uploads
async def add_my_gun(name: str, manufacturer: str, type: str, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = get_current_user().id
    add_gun(ownerId=user_id, name=name, manufacturer=manufacturer, type=type)


@router.post("/remove/{gun_id}")  # TODO: image uploads
async def remove_my_gun(gun_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    user_id = get_current_user().id
    if not get_gun_owner(gun_id) == user_id:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        raise credentials_exception
    remove_gun(gun_id)
