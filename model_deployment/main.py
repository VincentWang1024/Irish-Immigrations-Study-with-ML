import os
import torch
import torch.nn as nn
import pickle
import numpy as np
from flask import Flask, request, jsonify

savedModels={1: "CNN_Model_Torch.pth", 2: "LSTM_Model_Torch.pth", 'goemotion': "TransformerSentiment"}
class CNNModel(nn.Module):
    def __init__(self, embedding_matrix, num_classes):
        super(CNNModel, self).__init__()
        self.embedding = nn.Embedding.from_pretrained(torch.FloatTensor(embedding_matrix), freeze=True)
        self.conv1 = nn.Conv1d(100, 32, kernel_size=3)
        self.pool1 = nn.MaxPool1d(3)
        self.dropout1 = nn.Dropout(0.3)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3)
        self.pool2 = nn.MaxPool1d(5)
        self.dropout2 = nn.Dropout(0.3)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(384, 128)
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        embedded = self.embedding(x)
        embedded = embedded.permute(0, 2, 1)
        conv1_output = self.pool1(torch.relu(self.conv1(embedded)))
        conv1_output = self.dropout1(conv1_output)
        conv2_output = self.pool2(torch.relu(self.conv2(conv1_output)))
        conv2_output = self.dropout2(conv2_output)
        flattened = self.flatten(conv2_output)
        fc1_output = torch.relu(self.fc1(flattened))
        logits = self.fc2(fc1_output)
        return logits

class LSTMModel(nn.Module):
    def __init__(self, embedding_matrix, hidden_size=64, num_classes=3):
        super(LSTMModel, self).__init__()
        self.embedding = nn.Embedding.from_pretrained(torch.tensor(embedding_matrix, dtype=torch.float))
        self.embedding.requires_grad = False  # To freeze the embedding during training
        self.lstm1 = nn.LSTM(input_size=100, hidden_size=hidden_size, batch_first=True, bidirectional=False)
        self.dropout1 = nn.Dropout(0.5)
        self.lstm2 = nn.LSTM(input_size=hidden_size, hidden_size=hidden_size*2, batch_first=True, bidirectional=False)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(hidden_size*2, 50)
        self.dropout3 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(50, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        x, _ = self.lstm1(x)
        x = self.dropout1(x)
        x, _ = self.lstm2(x)
        x = self.dropout2(x)
        x = torch.relu(self.fc1(x[:, -1, :]))
        x = self.dropout3(x)
        x = self.fc2(x)
        return x
    

def pad_and_stack_embeddings(embeddings):
    max_length = max(len(embedding) for embedding in embeddings)
    padded_embeddings = []
    for embedding in embeddings:
        padding_length = max_length - len(embedding)
        padded_embedding = embedding + [0.0] * padding_length
        padded_embeddings.append(padded_embedding)
    padded_sequences = np.array(padded_embeddings)
    input_tensor = torch.tensor(padded_sequences, dtype=torch.long)
    return input_tensor


def prediction(input_tensor, model_id):
    with open('embedding_matrix.pickle', 'rb') as handle:
        embedding_matrix = pickle.load(handle)
    if model_id==1:
        loaded_model = CNNModel(embedding_matrix, num_classes=3)
    if model_id==2:
        loaded_model = LSTMModel(embedding_matrix, num_classes=3)
    loaded_model.load_state_dict(torch.load(savedModels[model_id]))
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    prediction_summary = {label: 0 for label in class_labels}
    loaded_model.eval()
    with torch.no_grad():
        val_outputs = loaded_model(input_tensor)
        val_predictions = torch.argmax(val_outputs, dim=1).tolist()

    predicted_classes = np.array(val_predictions)
        
    for predicted_class in predicted_classes:
        predicted_label = class_labels[predicted_class]
        prediction_summary[predicted_label] += 1
    return prediction_summary


app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        try:
            json_data = request.get_json()
            if 'embeddings' not in json_data or 'model_id' not in json_data:
                return jsonify({'status': 'error', 'message': 'embeddings and model_id are required fields'}), 400
            embeddings = json_data["embeddings"]
            modelID = json_data["model_id"]
            if embeddings is None or len(embeddings)==0:
                return jsonify({'status': 'error', 'message': 'Padded Sequence not found in request'}), 400
            input_tensor = pad_and_stack_embeddings(embeddings)
            prediction_summary = prediction(input_tensor, modelID)
            return jsonify(prediction_summary), 200
        except Exception as e:
            return jsonify({'error': str(e)})
    return "OK"

if __name__== "__main__":
    app.run(debug=True,host='0.0.0.0', port=8004)