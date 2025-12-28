from . import db
from datetime import datetime

class Roommate(db.Model):
    __tablename__ = 'Roommates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    image_path = db.Column(db.String(300), nullable=True)
    proof_path = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
