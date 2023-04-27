from flask import Flask, request, jsonify
from chatbot_utils import load_data, get_response
import json
import numpy as np
import random
import nltk
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)

lemmatizer = WordNetLemmatizer()

def clean_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_sentence(sentence)
    bag = {}
    for w in words:
        bag[w] = 0
        
    for w in sentence_words:
        if w in words:
            bag[w] = 1

    return np.array(list(bag.values()))

@app.route("/api/chatbot", methods=["POST"])
def chatbot_response():
    user_msg = request.json["message"]

    intents, tokenizer, model = load_data()

    response = get_response(user_msg, intents, tokenizer, model)

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
