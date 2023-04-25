from flask import Flask, render_template, request, jsonify
import numpy as np
from chatbot_utils import load_data, predict_class, get_response
from web_scraper import search

app = Flask(__name__)

words, classes, intents, model = load_data()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_msg = request.form["msg"]

    ints = predict_class(user_msg, words, classes, model)
    response = get_response(ints, intents, user_msg)

    if not response:
        search_results = search(user_msg)
        if search_results:
            response = f"I found the following information:\n"
            for result in search_results:
                response += f"{result['title']} - {result['link']}\n"
        else:
            response = "I'm sorry, I couldn't find any information on that topic."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run()
