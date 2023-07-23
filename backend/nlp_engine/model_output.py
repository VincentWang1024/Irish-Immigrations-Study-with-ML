from pymongo import MongoClient
import requests
import os
import torch
import torch.nn as nn
import tensorflow as tf
import numpy as np
import json
import os
import logging
from dotenv import load_dotenv
import tensorflow_text as text
import mysql.connector
import pandas as pd
from flask import Flask
import pickle
from flask import request, jsonify, Response
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost as xgb
from bertopic import BERTopic

app = Flask(__name__)

load_dotenv()

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

# mise en place
savedModels={1: "savedModels/CNN_Model_Torch.pth", 2: "savedModels/LSTM_Model_Torch.pth", 'goemotion': "savedModels/TransformerSentiment"}
MAX_EMOTIONS_LENGTH=4

@app.route("/api/callmodel", methods=['POST'])
def model_runner():
    data = request.json
    if 'jobID' not in data or 'model_id' not in data or 'median_time' not in data:
        return jsonify({'status': 'error', 'message': 'jobID and model_id are required fields'}), 400
    jobID = data.get('jobID')
    modelID = data.get('model_id')
    median_time = data.get('median_time')
    if modelID not in [1, 2, 3]:
        return jsonify({'status': 'error', 'message': 'Valid values for model_id are 1,2,3'}), 400
    
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    prediction_summary = {label: 0 for label in class_labels}
    testCorpus = get_preprocessed_text_from_db(jobID)
    topicCorpus = get_topic_text_from_db(jobID)

    if modelID == 1 or modelID == 2:
        vector_array = get_vector_data_from_db(jobID)
        prediction_summary = get_predictions_from_cnn_and_lstm(vector_array, prediction_summary, class_labels, modelID)
    elif modelID == 3:
        prediction_summary = get_predictions_from_xgb(testCorpus, prediction_summary, class_labels)

    prediction_summary = get_predictions_from_go_emotions(prediction_summary, testCorpus, jobID, median_time)
    sentiment_dict = {key: value for key, value in prediction_summary.items() if key not in ['emotions']}
    emotions_json = prediction_summary.get('emotions', {})

    try:
       topicsDetected = topic_detection(topicCorpus)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message':'Topic modelling error' }), 500

    if add_predictions_to_db(sentiment_dict, jobID) and add_emotions_results_to_db(emotions_json, jobID) and add_topic_results_to_db(topicsDetected,jobID):
        return jsonify({'status': 'success', 'message': 'Model execution completed successfully'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to execute model_runner, Persistence Error'}), 500


def add_predictions_to_db(prediction_summary, jobID):
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
    )
    try:
        with connection.cursor() as cursor:
            for label, ratio in prediction_summary.items():
                job_output_query = "INSERT INTO job_output (label, ratio, job_id) VALUES (%s, %s, %s)"
                cursor.execute(job_output_query, (label, ratio, jobID))
            connection.commit()
            return True
    except Exception as e:
        print(f"An error occurred while storing data: {str(e)}")
        return False
    finally:
        connection.close()

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

def get_topic_text_from_db(jobID):
    topicCorpus = []
    try: 
        connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
        )
        with connection.cursor() as cursor:
            cursor.execute('SELECT `sentence` FROM `topics_tokens` WHERE `job_id` = %s;', (jobID,))
            results = cursor.fetchall()
        for row in results:
           tokens_str = row[0]
           topicCorpus.append(tokens_str)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
    return topicCorpus

def generate_json_data(output, jobID, median_time):
    emotions = {
        0: ["anger", "annoyance", "disapproval"],
        1: ["joy", "amusement", "approval", "excitement"],
        2: ["neutral"],
        3: ["sadness", "disappointment", "embarrassment"],
        4: ["surprise", "realization", "confusion", "curiosity"]
    }

    num_classes = len(emotions)
    class_counts = np.zeros(num_classes, dtype=int)
    
    for label in output:
        class_counts[label] += 1
    
    total_samples = len(output)
    result = []
    
    for idx in range(num_classes):
        emotion_labels = ", ".join(emotions[idx])
        count = class_counts[idx]
        percentage = (count / total_samples) * 100
        result.append({emotion_labels: percentage})

    json_data = {
        "job_id": jobID,
        "result": result,
        "median_time":median_time
    }
    return json_data

def add_emotions_results_to_db(json_data, jobID):
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
    )
    try:
        with connection.cursor() as cursor:
            json_string = json.dumps(json_data)
            sql = "INSERT INTO goemotion_result_table (job_id, goemotion_result) VALUES (%s, %s)"
            cursor.execute(sql, (jobID, json_string))
            connection.commit()
            return True
    except Exception as e:
        print("An error occurred while storing data:", str(e))
        return False
    finally:
        connection.close()

def add_topic_results_to_db(topicsDetected, jobID):
    try:
        connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
        )
        with connection.cursor() as cursor:
            sql = "INSERT INTO topics_result_table (job_id, topic, probability) VALUES (%s, %s, %s)"
            for topic in topicsDetected:
                cursor.execute(sql, (jobID, topic[0], topic[1]))
            connection.commit()
            return True
    except Exception as e:
        print("An error occurred while storing topic data result:", str(e))
        return False
    finally:
        connection.close()

def topic_detection(topicCorpus):
    topic_model = BERTopic.load("savedModels/BERTOPIC_Model")
    topics, probs = topic_model.transform(topicCorpus)
    return topic_model.get_topic(0)

def get_predictions_from_cnn_and_lstm(padded_sequences, prediction_summary, class_labels, model_id):
    torch.manual_seed(42)
    np.random.seed(42)

    with open('embedding_matrix.pickle', 'rb') as handle:
        embedding_matrix = pickle.load(handle)
    input_tensor = torch.tensor(padded_sequences, dtype=torch.long)
    loaded_model.load_state_dict(torch.load(savedModels[int(model_id)]))
    if model_id==1:
        loaded_model = CNNModel(embedding_matrix, num_classes=3)
    if model_id==2:
        loaded_model = LSTMModel(embedding_matrix, num_classes=3)
    loaded_model.eval()

    with torch.no_grad():
        val_outputs = loaded_model(input_tensor)
        val_predictions = torch.argmax(val_outputs, dim=1).tolist()

    predicted_classes = np.array(val_predictions)
    
    for predicted_class in predicted_classes:
        predicted_label = class_labels[predicted_class]
        prediction_summary[predicted_label] += 1
    return prediction_summary

def get_predictions_from_xgb(testCorpus, prediction_summary, class_labels):
    with open('savedModels/xgb_tfidf.pkl', 'rb') as handle:
        vectorizer = pickle.load(handle)
    tfidf_features = vectorizer.transform(testCorpus)
    with open('savedModels/xgb_model.pkl', 'rb') as handle:
        xgb_model = pickle.load(handle)
    predictions = xgb_model.predict(tfidf_features)
    # values, counts = np.unique(predictions, return_counts=True)
    
    # for val, cnt in np.nditer([values,counts], flags=['buffered'], op_flags=['readonly','copy'], op_dtypes=['int64','int64']):
    #     label = class_labels[val]
    #     prediction_summary[label] = cnt
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

def get_predictions_from_go_emotions(prediction_summary, testCorpus, jobID, median_time):
    testCorpus = pd.Series(testCorpus)
    emotion_model = tf.keras.models.load_model(savedModels['goemotion'])
    emotion_predictions = emotion_model.predict(testCorpus)
    emotion_predictions = np.argmax(emotion_predictions, axis=1)
    json_result = generate_json_data(emotion_predictions, jobID, median_time)
    prediction_summary['emotions'] = json_result
    return prediction_summary

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8003)