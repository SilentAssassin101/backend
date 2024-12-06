from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from utils import execute_query
from auth import oauth2_scheme, get_current_user

already_exists_exception = HTTPException(
    status_code=status.HTTP_403_ALREADY_EXISTS,
    detail="Data Already Exists",
    headers={"WWW-Authenticate": "Bearer"},
)

not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def db_create_club(owner_id: int, name: str, address: str):
    if not db_check_club_name(name):
        execute_query(
            """INSERT INTO clubs (ownerId, name, address) VALUES (?,?,?)""",
            params=(owner_id, name, address)
        )
        id = db_check_club_name(name)
        db_add_club_member(club_id=id, member_id=owner_id)
    else:
        raise Exception("Club name already exists")


def db_check_club_name(club_name: str):
    execute_query(
        """SELECT * FROM clubs WHERE name=?""",
        params=(club_name),
        fetch=True
    )


def db_delete_club(club_id: int):
    execute_query(
        """DELETE FROM clubs WHERE id=?""",
        params=(club_id)
    )


def get_club_owner(club_id: int):
    execute_query(
        """SELECT ownerId FROM clubs WHERE id=?""",
        params=(club_id)
    )


def db_add_club_member(club_id: int, member_id: int):
    members = db_check_club_members(club_id)
    if member_id not in members:
        execute_query(
            """INSERT INTO clubMembers (clubId, memberId) VALUES (?,?)""",
            params=(club_id, member_id)
        )
    else:
        raise Exception("Club already contains memberId")


def db_check_club_members(club_id: int):
    return execute_query(
        """SELECT * FROM clubMembers WHERE clubId=?""",
        params=(club_id),
        fetch=True
    )


def db_check_club_exists(club_id: int):
    res = execute_query(
        """SELECT * FROM clubs WHERE id=?""",
        params=(club_id),
        fetch=True
    )
    if not res:
        return False
    else:
        return True


router = APIRouter()


@router.post("/create")
async def create_club(
    name: str,
    address: str,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = get_current_user(token).id
    if not db_check_club_name(club_name=name):
        db_create_club(owner_id=user_id, name=name, address=address)
    else:
        raise already_exists_exception


@router.post("/delete")
async def delete_club(
    club_id: int,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    if not db_check_club_exists(club_id=club_id):
        raise not_found_exception
    user_id = get_current_user(token).id
    if not get_club_owner(club_id) == user_id:
        raise credentials_exception
    db_delete_club(club_id)


@router.post("/join/{club_id}")
async def join_club(
    club_id: int,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    # TODO: check for invite
    user_id = get_current_user(token).id
    if user_id not in db_check_club_members(club_id=club_id):
        db_add_club_member(club_id=club_id, member_id=user_id)
    else:
        raise already_exists_exception
