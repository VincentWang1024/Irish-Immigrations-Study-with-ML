from pymongo import MongoClient
import requests
import os
import tensorflow as tf
import numpy as np
import json

def model_runner(jobID):
    try:
        client= MongoClient("mongodb://localhost:27017")
        db=client.get_database('Vector_Data')
        collection=db.preprocessed_data
    except Exception as e:
        print('Connection Failed')
        print(str(e))
        return
    vector_data = []
    alldocuments = collection.find({str(jobID): {'$exists': True}})
    for document in alldocuments:
        vector_data.append(document[str(jobID)])
    vector_array = np.array(vector_data)
    prediction_summary = predictions(vector_array)
    send_request(prediction_summary, jobID)
    

def predictions(padded_sequences):
    MAX_SEQUENCE_LENGTH = 100
    class_labels = ['Hateful', 'Non-Hateful', 'Neutral']
    #current_dir = os.path.dirname(os.path.abspath(__file__))
    #model_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'nlp code', 'savedModels', 'CNN_Model'))
    #relative_path = os.path.relpath(model_dir, current_dir)
    loaded_model = tf.keras.models.load_model("../nlp code/savedModels/CNN_Model")
    predictions = loaded_model.predict(padded_sequences)
    predicted_classes = np.argmax(predictions, axis=1)
    prediction_summary = {label: 0 for label in class_labels}
    for predicted_class in predicted_classes:
        predicted_label = class_labels[predicted_class]
        prediction_summary[predicted_label] += 1
    return prediction_summary

def send_request(prediction_summary, jobID):
    url = 'http://localhost:5000/model/result'
    prediction_json = json.dumps(prediction_summary)
    data = {
        'result': prediction_json,
        'job_id': jobID
    }
    print(data)
    #TODO: Connect to broker
    #response = requests.post(url, json=data)
    #print(f"Status Code: {response.status_code}, Response: {response.json()}")
    
    