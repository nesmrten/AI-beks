from torch import nn
from train_chatbot import ChatbotModel
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import json
import torch
import random
from web_scraper import search

lemmatizer = WordNetLemmatizer()

def load_data():
    with open("intents.json", "r") as file:
        intents = json.load(file)

    with open("words.json", "r") as file:
        words = json.load(file)

    with open("classes.json", "r") as file:
        classes = json.load(file)

    # Load the saved model
    model = ChatbotModel(len(words), 128, len(classes))
    model.load_state_dict(torch.load("chatbot_model.pth"))
    model.eval()

    return words, classes, intents, model

    return words, classes, intents, model

class ChatbotModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ChatbotModel, self).__init__()
        self.hidden_size = hidden_size
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        x = self.softmax(x)
        return x

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

    res = model(torch.tensor([bag], dtype=torch.float))[0].detach().numpy()
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
