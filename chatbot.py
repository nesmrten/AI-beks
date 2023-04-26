import json
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

lemmatizer = WordNetLemmatizer()

with open('intents.json') as file:
    data = json.load(file)

words = []
labels = []
docs = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        # tokenize each word in the pattern
        tokens = word_tokenize(pattern)
        words.extend(tokens)
        docs.append((tokens, intent['tag']))
        if intent['tag'] not in labels:
            labels.append(intent['tag'])

# lemmatize and lower case each word, remove duplicates and sort
words = sorted(list(set([lemmatizer.lemmatize(w.lower()) for w in words])))

# sort labels alphabetically
labels = sorted(labels)

# create training data
training = []
output_empty = [0] * len(labels)

for doc in docs:
    bag = []
    token_words = doc[0]
    token_words = [lemmatizer.lemmatize(word.lower()) for word in token_words]
    for w in words:
        bag.append(1) if w in token_words else bag.append(0)

    output_row = list(output_empty)
    output_row[labels.index(doc[1])] = 1
    training.append([bag, output_row])

# shuffle and convert to numpy array
random.shuffle(training)
training = np.array(training)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

# define model architecture
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(len(train_y[0]), activation='softmax'))

# compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# train model
model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

# save the model architecture and weights
model_json = model.to_json()
with open("chatbot_model.json", "w") as json_file:
    json_file.write(model_json)
model.save_weights("chatbot_model.h5")
print("Model saved to disk.")


def clean_sentence(sentence):
    tokens = word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in tokens]
    return sentence_words


def bow(sentence, words, show_details=True):
    sentence_words = clean_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"found in bag: {w}")
    return np.array(bag)


def predict_intent(sentence):
    # load the saved model
    json_file = open('chatbot_model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("chatbot_model.h5")
    print("Loaded model from disk")

    # predict output
    p = bow(sentence, words, show_details=False)
    prediction = loaded_model.predict(np.array([p]))[0]
    error_threshold = 0.25
    results = [[i, r] for i, r in enumerate(prediction) if r > error_threshold]

   # sort by probability score and only keep the most probable one
    results = [[i, r] for i, r in enumerate(predictions) if r > 0.25]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": labels[r[0]], "probability": str(r[1])})
    return return_list
