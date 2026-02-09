from fastapi import APIRouter , status , Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models.User import User
from app.schema.user_schema import UserSchema
from app.db.db import get_db
from app.services.user_services import create_user , get_users

router = APIRouter()

@router.get("/")
def get_user(db : Session =Depends(get_db)):
    try:
        users = get_users(db)
        return users
    except Exception as e:
        return JSONResponse(content=str(e) , status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post("/register")
def get_user(user :UserSchema, db : Session =Depends(get_db)):
    try:
        create_user(db , user)
        return JSONResponse(content="User Registered Successfully" , status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content=str(e) , status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)