import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import keras
import random
from web_scraper import search

lemmatizer = WordNetLemmatizer()

def load_data():
    with open("intents.json", "r") as file:
        intents = json.load(file)

    with open("words.pkl", "rb") as f: 
      words = pickle.load(f)

    with open("classes.pkl", "rb") as f: 
      classes = pickle.load(f)
      
    # Load the saved model
    model = keras.models.load_model("chatbot_model.h5")

    return words, classes, intents, model

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

def predict_class(user_msg, words, classes, model):
    bag = [0] * len(words)
    user_msg_words = nltk.word_tokenize(user_msg)
    user_msg_words = [lemmatizer.lemmatize(word.lower()) for word in user_msg_words]

    for w in user_msg_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    res = model.predict(np.array([bag]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

    return return_list

def get_response(ints, intents_json, user_msg):
    tag = ints[0]["intent"]
    probability = float(ints[0]["probability"])
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag and probability > 0.5:
            result = random.choice(i["responses"])
            break
        else:
            result = "I'm sorry, I didn't understand that. Could you please rephrase your question?"
    return result