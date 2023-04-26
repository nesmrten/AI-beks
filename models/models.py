
from app import db

from tensorflow.keras.models import load_model
model = load_model("chatbot_model.h5")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(50))
    token_expiration = db.Column(db.TIMESTAMP)