from fastapi import FastAPI
from app.api import auth
from app.db.db import Base  , engine
app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(router=auth.router , prefix='/api/user')