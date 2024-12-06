from utils import execute_query
from fastapi import APIRouter, Depends
from typing import Annotated
from auth import oauth2_scheme


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


def remove_gun(gunId: int):
    execute_query(
        """DELETE FROM guns WHERE id=? LIMIT 1""",
        params=(gunId)
    )


def get_guns_from_user(id: int):
    return execute_query(
        """SELECT * FROM guns WHERE ownerId=?""",
        params=(id),
        fetch=True
    )


router = APIRouter()


@router.get("/api/{user_id}/guns")
def get_user_guns(user_id: int, token: Annotated[str, Depends(oauth2_scheme)]):
    guns = get_guns_from_user(user_id)
    return {"user_id": user_id, "user_guns": guns}
