import random
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from tensorflow.keras.layers import TextVectorization

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize the database object
db = SQLAlchemy(app)

# Push an application context
app.app_context().push()

# Load the saved model
from tensorflow.keras.models import load_model
model = load_model("chatbot_model.h5")

# Load the intents file
with open("intents.json", "r") as file: 
    intents = json.load(file)

# Load the tokenizer object
vocab_size = 10000
vectorizer = TextVectorization(max_tokens=vocab_size, output_mode="int", output_sequence_length=30)

# Initialize the vectorizer
db.metadata.reflect(bind=db.engine, views=True)
questions = db.session.query(db.metadata.tables['questions'].columns.text).all()
questions = np.array(questions).ravel()
vectorizer.adapt(questions)

@app.route("/")
def home(): 
    return render_template("index.html")

@app.route("/chat")
def chat(): 
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    message = request.form["msg"]
    if message.strip() == "": 
        return jsonify({"response": "Please enter your message!"})

    message = np.array([message])
    message = vectorizer(message)
    prediction = model.predict(message)
    tag = intents[np.argmax(prediction)]["tag"]
    responses = intents[np.argmax(prediction)]["responses"]
    bot_response = random.choice(responses) 
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    # Define the table initializer here
    table_initializer = db.metadata.tables['questions'].insert().values(text="Hello", tag="greeting")
    db.session.execute(table_initializer)
    db.session.commit()

    app.run(debug=True)
