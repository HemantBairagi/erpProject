from app.schema.user_schema import UserSchema
from app.models.User import User

def create_user(db , user : UserSchema):
    user = User(name=user.name , email=user.email , password_hash=user.password , phone=user.phone , mobile=user.mobile)
    db.add(user)
    db.commit()
    db.refresh(user)

def get_users(db): 
    return db.query(User).all()
