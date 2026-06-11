from fastapi import APIRouter, Depends
from app.services.auth import logic_login
from app.core.config import settings
from app.schemas.auth import TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db_connection import connect_db

BASE_URL= settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/auth",
    tags= ["Authentication"]
)

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db : Session = Depends(connect_db)
):
    jwt_sig = logic_login(db= db, input_email=form_data.username, input_password=form_data.password)
    return {
        "access_token": jwt_sig,
        "token_type": "bearer"
    }


    