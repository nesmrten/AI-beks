import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import random
from web_scraper import search
from chatbot_utils import load_data, predict_class, get_response

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

def predict_class(sentence, words, classes, model):
    bag = bag_of_words(sentence, words)
    res = model.predict(np.array([bag]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(ints, intents, user_msg):
    tag = ints[0]["intent"]
    confidence = ints[0]["confidence"]
    min_confidence_threshold = 0.7  # Adjust this value according to your needs

    if confidence < min_confidence_threshold:
        search_results = search(user_msg)
        if search_results:
            response = f"I found some information related to your question:\n"
            for result in search_results:
                response += f"{result['title']} - {result['link']}\n"
            return response
        else:
            return "I'm sorry, I couldn't find any information on that topic. Please try another query."

    else:
        list_of_intents = intents["intents"]
        for i in list_of_intents:
            if i["tag"] == tag:
                result = random.choice(i["responses"])
                break
        return result

