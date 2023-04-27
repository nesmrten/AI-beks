import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from chatbot_model import ChatbotModel

# Set the device to run the model on
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the data from JSON files
def load_data():
    with open('intents.json', 'r') as file:
        intents = json.load(file)

    words = []
    classes = []
    documents = []
    ignore_letters = ['?', '.', ',', '!']

    # Loop through each sentence in the intents pattern and tokenize, lemmatize, and lowercase each word
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # Apply the lemmatization and lowercase to each word, and remove duplicates from the list of words
    words = [WordNetLemmatizer().lemmatize(word.lower()) for word in words if word not in ignore_letters]
    words = sorted(list(set(words)))

    # Remove duplicates from the list of classes
    classes = sorted(list(set(classes)))

    training = []
    output_empty = [0] * len(classes)

    # Loop through each sentence and create a bag of words for each one
    for document in documents:
        bag = []

        word_patterns = document[0]
        word_patterns = [WordNetLemmatizer().lemmatize(word.lower()) for word in word_patterns]

        for word in words:
            bag.append(1) if word in word_patterns else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1

        training.append([bag, output_row])

    # Shuffle the data and convert it to a numpy array
    np.random.shuffle(training)
    training = np.array(training)

    # Split the training and testing data
    train_x = list(training[:,0])
    train_y = list(training[:,1])

    return words, classes, train_x, train_y

# Train the model
def train_model(model, train_x, train_y):
    loss_function = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.0001)

    for epoch in range(1000):
        epoch_loss = 0
        for i, (inputs, labels) in enumerate(zip(train_x, train_y)):
            inputs = torch.tensor(inputs, dtype=torch.float).to(device)
            labels = torch.tensor(np.argmax(labels), dtype=torch.long).to(device)

            # Zero the gradients and perform forward and backward passes
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_function(outputs.unsqueeze(0), labels.unsqueeze(0))
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        if epoch % 100 == 0:
            print(f'Epoch {epoch+1}, loss={epoch_loss:.4f}')

    print(f'Final loss: {epoch_loss:.4f}')

# Save the trained model
def save_model(model, words, classes):
    # Save the trained model
    torch.save(model.state_dict(), 'chatbot_model.pt')

    # Save the words and classes
    with open('words.json', 'w') as file: 
        with open('classes.json', 'w') as file: 
            json.dump(classes, file)
        
# Define the chatbot response function
def get_response(ints, intents_json, message):
    tag = ints.argmax()
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

# Define the function to predict the class of a sentence
def predict_class(sentence, words, classes, model):
    # Tokenize the sentence and convert it to a bag of words
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [WordNetLemmatizer().lemmatize(word.lower()) for word in sentence_words]
    bag = [0] * len(words)
    for s in sentence_words:
        for i, word in enumerate(words):
            if word == s:
                bag[i] = 1

    # Convert the bag of words to a tensor and make a prediction
    input_data = torch.tensor(bag, dtype=torch.float).to(device)
    output = model(input_data)
    _, predicted = torch.max(output, dim=0)
    return predicted

# Define the main function to run the chatbot
def run_chatbot():
    # Load the data and create the model
    words, classes, train_x, train_y = load_data()
    input_size = len(words)
    hidden_size = 8
    output_size = len(classes)
    model = ChatbotModel(input_size, hidden_size, output_size).to(device)

    # Train the model and save it
    train_model(model, train_x, train_y)
    save_model(model, words, classes)

    # Define the Flask app and route to the chatbot response function
    app = Flask(__name__)
    @app.route('/get', methods=['POST'])
    def chatbot_response():
        message = request.json['message']
        ints = predict_class(message, words, classes, model)
        response = get_response(ints, intents, message)
        return jsonify({'response': response})

    # Run the app
    app.run(debug=True)

if __name__ == '__main__':
    run_chatbot()
