from pydantic import BaseModel
class UserSchema(BaseModel):
    name : str
    email : str
    password : str
    phone : str | None
    mobile : str | None
