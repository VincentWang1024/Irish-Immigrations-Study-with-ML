import torch
import torch.nn as nn
import pickle
import numpy as np
from dotenv import load_dotenv
import xgboost as xgb
from pymongo import MongoClient
import mysql.connector
from flask import Flask, request, jsonify
import os

load_dotenv()

savedModels={1: "CNN_Model_Torch.pth", 2: "LSTM_Model_Torch.pth"}

app = Flask(__name__)


"""
Model_id mapping:-
1=CNN
2=LSTM
3=XGBOOST
4=CNN+XGBOOST
5=LSTM+XGBOOST
6=CNN+LSTM
"""
@app.route("/predict", methods=["POST"])
def index():
    if request.method=="POST":
        try:
            json_data = request.get_json()
            if 'model_id' not in json_data:
                return jsonify({'status': 'error', 'message': 'data and model_id are required fields'}), 400
            modelID = json_data["model_id"]
            job_id = json_data["job_id"]
            if job_id is None or job_id=="":
                return jsonify({'status': 'error', 'message': 'job_id not found in request'}), 400
            if modelID==1 or modelID==2 or modelID==6:
                embeddings = get_vector_data_from_db(job_id)
                input_tensor = pad_and_stack_embeddings(embeddings)
                prediction_summary = prediction(modelID, input_tensor=input_tensor)
                for key, value in prediction_summary.items():
                    if isinstance(value, np.ndarray):
                        prediction_summary[key] = value.tolist()
                return jsonify(prediction_summary), 200
            elif modelID==3:
                testCorpus=get_preprocessed_text_from_db(job_id)
                if testCorpus is None or len(testCorpus)==0:    
                    return jsonify({'status': 'error', 'message': 'test_corpus not found in DB'}), 400
                prediction_summary = prediction(modelID, testCorpus=testCorpus)
                for key, value in prediction_summary.items():
                    if isinstance(value, np.ndarray):
                        prediction_summary[key] = value.tolist()
                return jsonify(prediction_summary), 200
            elif modelID==4 or modelID==5:
                embeddings = get_vector_data_from_db(job_id)
                testCorpus=get_preprocessed_text_from_db(job_id)
                if embeddings is None or len(embeddings)==0:
                    return jsonify({'status': 'error', 'message': 'Padded Sequence not found in DB'}), 400
                if testCorpus is None or len(testCorpus)==0:    
                    return jsonify({'status': 'error', 'message': 'test_corpus not found in DB'}), 400
                input_tensor = pad_and_stack_embeddings(embeddings)
                prediction_summary = prediction(modelID, input_tensor=input_tensor, testCorpus=testCorpus)
                for key, value in prediction_summary.items():
                    if isinstance(value, np.ndarray):
                        prediction_summary[key] = value.tolist()
                return jsonify(prediction_summary), 200
            else:
               return jsonify({'status': 'error', 'message': 'Received invalid modelId'}), 400 

        except Exception as e:
            return jsonify({'error': str(e)})
    return "OK"

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
    
    def __str__(self):
        return "CNNModel Loaded"

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
    
    def __str__(self):
        return "LSTM Loaded"
    

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

def get_preprocessed_text_from_db(jobID):
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
    )

    cursor = connection.cursor()
    cursor.execute('SELECT `sentence` FROM `emotions_texts` WHERE `job_id` = %s;', (jobID,))
    results = cursor.fetchall()
    sentences = [row[0] for row in results]
    return sentences

def get_vector_data_from_db(jobID):
    try:
        CONNECTION_STRING = os.getenv('MONGO_URI')
        client= MongoClient(CONNECTION_STRING)
        db=client.get_database('Vector_Data')
        collection=db.preprocessed_data
        alldocuments = collection.find({str(jobID): {'$exists': True}})
        vector_data = []
        for document in alldocuments:
            vector_data.append(document[str(jobID)])
        if len(vector_data) == 0:
            raise Exception('No vector data found in MongoDB')
        vector_array = np.array(vector_data)
        return vector_array       
    except Exception as e:
        print('Connection Failed')
        print(str(e))
        return jsonify({'status': 'error', 'message': 'No vector data found in MongoDB'}), 404

def prediction(model_id, input_tensor=None, testCorpus=None):
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    prediction_summary = {label: 0 for label in class_labels}  
    with open('embedding_matrix.pickle', 'rb') as handle:
        embedding_matrix = pickle.load(handle) 
    if model_id==1:
        loaded_model = CNNModel(embedding_matrix, num_classes=3)
        prediction_summary = predict_with_embedding(loaded_model, prediction_summary, model_id, input_tensor, class_labels)
        return prediction_summary
    elif model_id==2:
        loaded_model = LSTMModel(embedding_matrix, num_classes=3)
        prediction_summary = predict_with_embedding(loaded_model, prediction_summary, model_id, input_tensor, class_labels)
        return prediction_summary
    elif model_id==3:
        prediction_summary = predict_with_xgboost(prediction_summary, model_id)
        return prediction_summary
    elif model_id == 4:
        loaded_cnn_model = CNNModel(embedding_matrix, num_classes=3)
        prediction_summary_cnn = predict_with_embedding(loaded_cnn_model, prediction_summary.copy(), 1, input_tensor, class_labels)
        prediction_summary_xgb = predict_with_xgboost(prediction_summary.copy(), testCorpus)
        combined_summary = combine_results([prediction_summary_cnn, prediction_summary_xgb])
        return combined_summary
    elif model_id == 5:
        loaded_lstm_model = LSTMModel(embedding_matrix, num_classes=3)
        prediction_summary_lstm = predict_with_embedding(loaded_lstm_model, prediction_summary.copy(), 2, input_tensor, class_labels)
        prediction_summary_xgb = predict_with_xgboost(prediction_summary.copy(), testCorpus)
        combined_summary = combine_results([prediction_summary_lstm, prediction_summary_xgb])
        return combined_summary
    elif model_id == 6:
        loaded_cnn_model = CNNModel(embedding_matrix, num_classes=3)
        loaded_lstm_model = LSTMModel(embedding_matrix, num_classes=3)
        prediction_summary_cnn = predict_with_embedding(loaded_cnn_model, prediction_summary.copy(), 1, input_tensor, class_labels)
        prediction_summary_lstm = predict_with_embedding(loaded_lstm_model, prediction_summary.copy(), 2, input_tensor, class_labels)
        combined_summary = combine_results([prediction_summary_cnn, prediction_summary_lstm])
        return combined_summary
    else:
        raise ValueError("Invalid model_id. Please choose a valid model_id from 1 to 6.")
    

def combine_results(predictions_list):
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    combined_summary = {label: 0 for label in class_labels}

    for predictions in predictions_list:
        for label, count in predictions.items():
            combined_summary[label] += count

    return combined_summary


def predict_with_embedding(loaded_model, prediction_summary, model_id, input_tensor, class_labels):
    torch.manual_seed(42)
    np.random.seed(42)
    loaded_model.load_state_dict(torch.load(savedModels[model_id]))
    loaded_model.eval()
    with torch.no_grad():
        val_outputs = loaded_model(input_tensor)
        val_predictions = torch.argmax(val_outputs, dim=1).tolist()
    predicted_classes = np.array(val_predictions)
    for predicted_class in predicted_classes:
        predicted_label = class_labels[predicted_class]
        prediction_summary[predicted_label] += 1
    return prediction_summary

def predict_with_xgboost(prediction_summary, testCorpus):
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    with open('xgb_tfidf.pkl', 'rb') as handle:
        vectorizer = pickle.load(handle)
    tfidf_features = vectorizer.transform(testCorpus)
    with open('xgb_model.pkl', 'rb') as handle:
        xgb_model = pickle.load(handle)
    predictions = xgb_model.predict(tfidf_features)
    count_zeros = 0
    count_ones = 0
    count_twos = 0
    for pred in predictions.flat:
        if pred == 0:
            count_zeros = count_zeros + 1
        elif pred == 1:
            count_ones = count_ones + 1
        elif pred == 2:
            count_twos = count_twos + 1
    prediction_summary[class_labels[0]] = count_zeros
    prediction_summary[class_labels[1]] = count_ones
    prediction_summary[class_labels[2]] = count_twos
    return prediction_summary


if __name__== "__main__":
    app.run(debug=True,host='0.0.0.0', port=8004)