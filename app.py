from flask import Flask, request, jsonify
from keras.models import load_model
import json
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import random

app = Flask(__name__)

lemmatizer = WordNetLemmatizer()

def clean_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    return np.array(bag)

@app.route("/api/chatbot", methods=["POST"])
def get_response():
    user_msg = request.json["message"]

    with open("intents.json", "r") as file:
        intents = json.load(file)

    with open("words.json", "r") as file:
        words = json.load(file)

    # Load the classes
    with open("classes.json", "r") as file:
        classes = json.load(file)

    # Load the saved model
    model = load_model("chatbot_model.h5")

    # Predict the intent of the user's message
    bag = bag_of_words(user_msg, words)
    res = model.predict(np.array([bag]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

    tag = return_list[0]["intent"]
    list_of_intents = intents["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break

    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
