from pymongo import MongoClient
import requests
import os
import tensorflow as tf
import numpy as np
import json
import os
from dotenv import load_dotenv
import tensorflow_text as text
import mysql.connector
import pandas as pd
from flask import Flask
from flask import request, jsonify, Response

app = Flask(__name__)

load_dotenv()

savedModels={1: "savedModels/CNN_Model", 2: "savedModels/LSTM_Model", 'goemotion': "savedModels/TransformerSentiment"}
MAX_EMOTIONS_LENGTH=4

@app.route("/api/callmodel", methods=['POST'])
def model_runner():
    modelID, jobID = get_modelid_and_jobid_from_json()
    vector_array = get_vector_data_from_db(modelID, jobID)
    prediction_summary = get_predictions_for_CNN_and_LSTM(vector_array, modelID)
    testCorpus = get_preprocessed_text_from_db(jobID)
    prediction_summary = get_predictions_for_go_emotions(testCorpus, prediction_summary, jobID)
    sentiment_dict = {key: value for key, value in prediction_summary.items() if key not in ['emotions']}
    emotions_json = prediction_summary.get('emotions', {})
    if add_predictions_to_db(sentiment_dict, jobID) and add_emotions_results_to_db(emotions_json, jobID):
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

def generate_json_data(output, jobID):
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
        "result": result
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

def get_predictions_for_CNN_and_LSTM(padded_sequences, model_id):
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    loaded_model = tf.keras.models.load_model(savedModels[int(model_id)])   
    predictions = loaded_model.predict(padded_sequences)
    predicted_classes = np.argmax(predictions, axis=1)
    prediction_summary = {label: 0 for label in class_labels}
    for predicted_class in predicted_classes:
        predicted_label = class_labels[predicted_class]
        prediction_summary[predicted_label] += 1
    return prediction_summary

def get_predictions_for_go_emotions(prediction_summary, testCorpus, jobID):
    testCorpus = pd.Series(testCorpus)
    emotion_model = tf.keras.models.load_model(savedModels['goemotion'])
    EmotionPredictions = emotion_model.predict(testCorpus)
    EmotionPredictions = np.argmax(EmotionPredictions, axis=1)
    jsonResult=generate_json_data(EmotionPredictions, jobID)
    prediction_summary['emotions']=jsonResult
    return prediction_summary

def get_vector_data_from_db(modelID, jobID):
    try:
        if modelID == 1 or modelID == 2:
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

def get_modelid_and_jobid_from_json():
    data = request.json
    if 'jobID' not in data or 'model_id' not in data:
        return jsonify({'status': 'error', 'message': 'jobID and model_id are required fields'}), 400
    jobID = data.get('jobID')
    modelID = data.get('model_id')
    if modelID not in [1, 2, 3, 4]:
        return jsonify({'status': 'error', 'message': 'Valid values for model_id are 1,2,3,4'}), 400
    return modelID, jobID

if __name__ == '__main__':
    app.run(debug = True, port=8003)