from views.auth import auth
from views.main import main
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from models.model import db, init_app as init_db
from chatbot_utils import load_data, predict_class, get_response
import torch

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Stargatesg-1aio!#$'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

init_db(app)

with app.app_context():
    db.create_all()

app.register_blueprint(main)
app.register_blueprint(auth)

@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return User.query.get(int(user_id))

# Load chatbot data
words, classes, intents, chatbot_model = load_data()

@app.route("/api/chatbot", methods=["POST"])
def chatbot_response():
    user_msg = request.json["message"]
    ints = predict_class(user_msg, words, classes, chatbot_model)
    res = get_response(ints, intents, user_msg)
    return jsonify({"response": res})

if __name__ == '__main__':
    app.run(debug=True)
