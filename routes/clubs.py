from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from utils import execute_query
from auth import oauth2_scheme, get_current_user

conflict_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
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


def db_delete_club(club_id: int):  # TODO: remove all members after
    execute_query(
        """DELETE FROM clubs WHERE id=?""",
        params=(club_id)
    )
    execute_query(
        """DELETE FROM clubMembers WHERE clubId=?""",
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


def db_remove_club_member(club_id: int, member_id: int):
    execute_query(
        """DELETE FROM clubMembers WHERE clubIdd=? AND memberId=?""",
        params=(club_id, member_id)
    )


def db_check_invite(club_id: int, user_id: int):
    return execute_query(
        """SELECT * FROM clubInvites WHERE clubId=? AND userId=? LIMIT 1""",
        params=(club_id, user_id),
        fetch=True
    )


def db_send_invite(club_id: int, user_id: int):
    if not db_check_invite(club_id, user_id):
        execute_query(
            """INSERT INTO clubInvites (clubId, userId) VALUES (?,?)""",
            params=(club_id, user_id)
        )


def db_remove_invite(club_id: int, user_id: int):
    if db_check_invite(club_id, user_id):
        execute_query(
            """DELETE FROM clubInvites WHERE clubId=? AND userId=?""",
            params=(club_id, user_id)
        )


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
        raise conflict_exception


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
    user_id = get_current_user(token).id
    if not db_check_invite(club_id, user_id):
        raise credentials_exception
    if user_id not in db_check_club_members(club_id=club_id):
        db_add_club_member(club_id=club_id, member_id=user_id)
    else:
        raise conflict_exception


@router.post("/leave/{club_id}")
async def leave_club(
    club_id: int,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = get_current_user(token).id
    if user_id in db_check_club_members(club_id) and user_id not in get_club_owner(club_id):
        db_remove_club_member(club_id, member_id=user_id)
    else:
        raise not_found_exception


@router.post("/invite")
async def invite_club(
    club_id: int,
    invitee_id: int,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = get_current_user(token).id
    if user_id not in get_club_owner(club_id):
        raise credentials_exception
    db_send_invite(club_id, user_id=invitee_id)
