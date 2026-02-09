from fastapi import FastAPI
from app.api import user_router
from app.db.db import Base  , engine
app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(router=user_router.router , prefix='/api/user')