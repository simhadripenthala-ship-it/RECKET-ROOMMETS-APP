from models.user import User
from models import db

def create_user(username, email, password, contact_number=None):
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return None
    user = User(username=username, email=email, password=password, contact_number=contact_number)
    db.session.add(user)
    db.session.commit()
    return user

def get_current_user():
    from flask import session
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None
