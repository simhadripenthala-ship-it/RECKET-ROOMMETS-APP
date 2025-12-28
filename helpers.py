# utils/helpers.py
from flask import session
from models.user import User
from models import db

def create_user(username, email, password, contact_number=None):
    """
    Create a new user if username or email does not exist.
    Returns the user object if created successfully, else None.
    """
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return None

    new_user = User(username=username, password=password, email=email, contact_number=contact_number)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def get_current_user():
    """
    Get the currently logged-in user from the session.
    """
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)
