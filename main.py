from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import (
    Token,
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token
)
from testing import activate_all_testing
from routes.guns import router as guns_router
from routes.users import router as users_router

testing = True
if testing:
    activate_all_testing()


app = FastAPI()

app.include_router(guns_router, prefix="/guns", tags=["guns"])
app.include_router(users_router, prefix="/users", tags=["users"])


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
