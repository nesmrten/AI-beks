import random
import json
import numpy as np
from tensorflow.keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk
from chatbot_utils import search

class ChatBot:
    def __init__(self, model_path, intents_path):
        self.model_path = model_path
        self.intents_path = intents_path
        self.lemmatizer = WordNetLemmatizer()
        self.model = None
        self.intents = None
        self.words = None
        self.classes = None
        self.load_data()

    def load_data(self):
        with open('words.json', 'r') as f:
            self.words = json.load(f)
        with open('classes.json', 'r') as f:
            self.classes = json.load(f)
        with open(self.intents_path, 'r') as f:
            self.intents = json.load(f)
        self.model = load_model(self.model_path)

    def clean_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bag_of_words(self, sentence, words):
        sentence_words = self.clean_sentence(sentence)
        bag = [0] * len(words)
        for w in sentence_words:
            for i, word in enumerate(words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)

    def predict_class(self, user_msg):
        bag = self.bag_of_words(user_msg, self.words)
        res = self.model.predict(np.array([bag]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.classes[r[0]], "probability": str(r[1])})
        return return_list

    def get_response(self, user_msg):
        ints = self.predict_class(user_msg)
        tag = ints[0]["intent"]
        probability = float(ints[0]["probability"])
        for intent in self.intents["intents"]:
            if intent["tag"] == tag and probability > 0.5:
                result = random.choice(intent["responses"])
                if "search" in intent:
                    results = search(intent["search"], user_msg)
                    if results:
                        result = result.format(results[0])
                    else:
                        result = "Sorry, I couldn't find any results for that."
                break
        else:
            result = "I'm sorry, I didn't understand that. Could you please rephrase your question?"
        return result
