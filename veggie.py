from . import db
from datetime import datetime

class Veggie(db.Model):
    __tablename__ = 'veggie'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    quantity_kg = db.Column(db.Float, default=0)
    cost_per_kg = db.Column(db.Float, default=0)
    curry_recipe = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
