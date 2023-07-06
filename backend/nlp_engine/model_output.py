from pymongo import MongoClient
import requests
import os
import tensorflow as tf
import numpy as np
import json
import os
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
from flask import Flask
from flask import request, jsonify, Response
app = Flask(__name__)

load_dotenv()

# mise en place
savedModels={1: "savedModels/CNN_Model", 2: "savedModels/LSTM_Model", 'goemotion': "savedModels/TransformerSentiment"}
@app.route("/api/callmodel", methods=['POST'])
def model_runner():
    data = request.json
    if 'jobID' not in data or 'model_id' not in data:
        return jsonify({'status': 'error', 'message': 'jobID and model_id are required fields'}), 400
    jobID = data.get('jobID')
    modelID = data.get('model_id')
    if modelID not in [1, 2]:
        return jsonify({'status': 'error', 'message': 'Valid values for model_id are 1,2'}), 400
    vector_data = []
    try:
        CONNECTION_STRING = os.getenv('MONGO_URI')
        client= MongoClient(CONNECTION_STRING)
        db=client.get_database('Vector_Data')
        collection=db.preprocessed_data
        testCorpus = GetPreprocText(jobID)
        alldocuments = collection.find({str(jobID): {'$exists': True}})
        for document in alldocuments:
            vector_data.append(document[str(jobID)])
        vector_array = np.array(vector_data)
        if len(vector_data) == 0:
            raise Exception('No vector data found in MongoDB')
    except Exception as e:
        print('Connection Failed')
        print(str(e))
        return jsonify({'status': 'error', 'message': 'No vector data found in MongoDB'}), 404
    prediction_summary = predictions(vector_array, testCorpus, modelID)
    if SQLConnector(prediction_summary, jobID):
        return jsonify({'status': 'success', 'message': 'Model execution completed successfully'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to execute model_runner'}), 500


def SQLConnector(prediction_summary, jobID):
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
    )

    try:
        with connection.cursor() as cursor:
            for label, ratio in prediction_summary.items():
                sql = "INSERT INTO job_output (label, ratio, job_id) VALUES (%s, %s, %s)"
                cursor.execute(sql, (label, ratio, jobID))

            for emotions_list in prediction_summary.get('emotions', []):
                sql = "INSERT INTO emotions_table (job_id, emotionsList) VALUES (%s, %s)"
                cursor.execute(sql, (jobID, ', '.join(emotions_list)))

            connection.commit()
            return True

    except Exception as e:
        print(f"An error occurred while storing data: {str(e)}")
        return False

    finally:
        connection.close()

def GetPreprocText(jobID):
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

def predictions(padded_sequences, testCorpus, model_id):
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    loaded_model = tf.keras.models.load_model(savedModels[int(model_id)])
    print("loaded CNN")
    emotion_model = tf.keras.models.load_model(savedModels['goemotion'])
    print("loaded GoEmotions")
    predictions = loaded_model.predict(padded_sequences)
    predicted_classes = np.argmax(predictions, axis=1)
    prediction_summary = {label: 0 for label in class_labels}
    for predicted_class in predicted_classes:
        predicted_label = class_labels[predicted_class]
        prediction_summary[predicted_label] += 1
    testCorpus = pd.Series(testCorpus)
    EmotionPredictions = emotion_model.predict(testCorpus)
    EmotionPredictions = np.argmax(EmotionPredictions, axis=1)
    reverse_mapping = {
        0: ["anger", "annoyance", "disapproval"],
        1: ["disgust"],
        2: ["fear", "nervousness"],
        3: ["joy", "amusement", "approval", "excitement", "gratitude", "love", "optimism", "relief", "pride", "admiration", "desire", "caring"],
        4: ["sadness", "disappointment", "embarrassment", "grief", "remorse"],
        5: ["surprise", "realization", "confusion", "curiosity"],
        6: ["neutral"]
    }
    predicted_emotions = [reverse_mapping[prediction] for prediction in EmotionPredictions]
    prediction_summary['emotions']=predicted_emotions
    return prediction_summary


if __name__ == '__main__':
    app.run(debug = True, port=5003)
# model_runner('a4ca21c2-1444-11ee-9dcf-fefcbf0ffb95')