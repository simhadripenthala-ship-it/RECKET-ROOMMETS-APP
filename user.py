from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

    # ------------------ Constructor ------------------
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    # ------------------ Password Handling ------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ------------------ Database Helpers ------------------
    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Failed to save user: {e}")
            return None

    @staticmethod
    def create_user(username, password):
        """Create a new user if username not already exists."""
        if User.query.filter_by(username=username).first():
            print("[INFO] Username already exists.")
            return None

        new_user = User(username=username, password=password)
        return new_user.save_to_db()

    # ------------------ Representation ------------------
    def __repr__(self):
        return f"<User {self.username}>"
