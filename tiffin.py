from datetime import datetime
from models import db

class Tiffin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe = db.Column(db.String(100), nullable=False)
    week_day = db.Column(db.String(20))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
