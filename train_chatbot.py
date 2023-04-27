import json
import numpy as np
import nltk
import torch
import torch.nn as nn
import torch.optim as optim
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelBinarizer

nltk.download("punkt")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()

with open("intents.json") as file:
    intents = json.load(file)

words = []
classes = []
documents = []
ignore_letters = ["!", "?", ",", "."]

for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])

words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(list(set(words)))

classes = sorted(list(set(classes)))

with open("words.json", "w") as f:
    json.dump(words, f)

with open("classes.json", "w") as f:
    json.dump(classes, f)

training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

np.random.shuffle(training)
training = np.array(training, dtype=object)

train_x = np.array(list(training[:, 0]))
train_y = np.array(list(training[:, 1]))

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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

input_size = len(train_x[0])
output_size = len(train_y[0])
hidden_size = 128

model = ChatbotModel(input_size, hidden_size, output_size).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, nesterov=True)

train_x = torch.tensor(train_x, dtype=torch.float32).to(device)
train_y = torch.tensor(train_y, dtype=torch.long).to(device)

epochs = 200
batch_size = 5

for epoch in range(epochs):
    for i in range(0, len(train_x), batch_size):
        batch_x = train_x[i:i + batch_size]
        batch_y = train_y[i:i + batch_size]

        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, torch.max(batch_y, 1)[1])
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}")

torch.save(model.state_dict(), "chatbot_model.pth")
       
