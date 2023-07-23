# imports
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('omw-1.4')
import re
import pickle
from langdetect import detect
import tensorflow as tf
from pymongo import MongoClient
import mysql.connector
from flask import Flask
from flask import request, jsonify
from flask import Response
import requests
app = Flask(__name__)

# mise en place
MAX_SEQUENCE_LENGTH=100

@app.route("/api/preprocess", methods=['POST'])
def runner():
    data = request.json
    if 'jobID' not in data or 'model_id' not in data or 'median_time' not in data:
        return jsonify({'status': 'error', 'message': 'jobID, model_id, and median_time are required fields'}), 400
    jobID = data.get('jobID')
    modelID = data.get('model_id')
    median_time = data.get('median_time')
    if modelID not in [1, 2, 3]:
        return jsonify({'status': 'error', 'message': 'Valid values for model_id are 1,2,3'}), 400
    try:
        comments = get_comments_from_db(jobID)
        if modelID == 1 or modelID == 2:
            padded_sequences = generate_embeddings(comments)
            push_mongo(padded_sequences, jobID)

        testCorpus= perform_preprocessing(comments)
        add_corpus_to_db(testCorpus, jobID)
        topicCorpus=perform_preprocessing_topic_text(comments) 
        add_topicCorpus_to_db(topicCorpus, jobID)
        model_runner_url = 'http://nlp_service:8003/api/callmodel'
        response = requests.post(model_runner_url, json={'jobID': jobID, 'model_id': modelID, 'median_time': median_time})
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Preprocessing completed and model_runner executed successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Received bad status from model_runner'}), 500
    except Exception as e:
        print("An error occurred during preprocessing:", str(e))
        return jsonify({'status': 'error', 'message': 'Preprocessing runner failed'}), 500

def emoji_dictionary():
    emoji_dict = {}
    with open('emoji.txt', 'r', encoding='latin-1') as emoji_file:
        for line in emoji_file:
            line = line.strip()
            if line:
                emoji, value = line.split('\t')
                emoji_dict[emoji] = int(value)
    return emoji_dict

def replace_emojis(text, emoji_dict):
    for emoji, value in emoji_dict.items():
        if value == 1:
            text = re.sub(re.escape(emoji), 'support', text)
        elif value == -1:
            text = re.sub(re.escape(emoji), 'illegal', text)
    return text
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None
    
def preprocess_text(text):  
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    words = word_tokenize(text)
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    lemmatizer = WordNetLemmatizer()
    tagged = pos_tag(words)
    words = [lemmatizer.lemmatize(word, pos=get_wordnet_pos(pos)) if get_wordnet_pos(pos) else word for word, pos in tagged]
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    filtered_text = ' '.join(filtered_words)
    return filtered_text 

def preprocess_topic_text(text):  
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    topicCorpus = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    tagged_topic=pos_tag(topicCorpus)
    topicCorpus = [lemmatizer.lemmatize(word, pos=get_wordnet_pos(pos)) if get_wordnet_pos(pos) else word for word, pos in tagged_topic]
    stop_words = set(stopwords.words('english'))
    topic_text = [word for word in topicCorpus if word not in stop_words]
    topic_corpus = ' '.join(topic_text)
    return topic_corpus
    

def get_comments_from_db(jobID):
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
    )
    cursor = connection.cursor()
    cursor.execute('SELECT `comments` FROM `usercomments` WHERE `jobid` = %s;', (jobID,))
    results = cursor.fetchall()
    sentences = [row[0] for row in results]
    return sentences

def add_corpus_to_db(testCorpus, jobID):
    connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
    )
    try:
        cursor = connection.cursor()
        sentences = []
        for sentence in testCorpus:
            sql = "INSERT INTO emotions_texts (job_id, sentence) VALUES (%s, %s)"
            cursor.execute(sql, (jobID, sentence))
            sentences.append(sentence)
        connection.commit()
    except Exception as e:
        print(f"An error occurred while storing data: {str(e)}")
        return []

    finally:
        connection.close()
    
def add_topicCorpus_to_db(topicCorpus, jobID):
    try:
        connection = mysql.connector.connect(
        user=os.getenv('MYSQL_ROOT_USERNAME'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DB')
        )
        with connection.cursor() as cursor:
            for sentence in topicCorpus:
                insert_query = 'INSERT INTO topics_tokens (job_id, sentence) VALUES (%s, %s)'
                cursor.execute(insert_query,(jobID, sentence))
            connection.commit()
    except Exception as e:
        print(f"An error occurred while storing topic data: {str(e)}")
        return []

    finally:
        connection.close()

def generate_embeddings(comments):            
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    testCorpus = perform_preprocessing(comments)
    input_sequences = tokenizer.texts_to_sequences(testCorpus)
    padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(input_sequences, maxlen=MAX_SEQUENCE_LENGTH)
    return padded_sequences
 
def push_mongo(padded_sequences, jobID):
    try:
        CONNECTION_STRING = os.getenv('MONGO_URI')
        client= MongoClient(CONNECTION_STRING)
        db=client.get_database('Vector_Data')
        collection=db.preprocessed_data
        for row in padded_sequences:
            document = {str(jobID):row.tolist()}
            collection.insert_one(document)
        print("Data Pushed Successfully To MongoDB")
    except Exception as e:
        print("Error while inserting data to MongoDB:")
        print(str(e))

def perform_preprocessing(comments):
    emoji_dict=emoji_dictionary()
    testCorpus=[]
    for text in comments:
        try:
            lang = detect(text)
        except:
            lang = ""
        if lang == "en":
            newText = text.strip()
            newText = replace_emojis(newText, emoji_dict)
            newText = preprocess_text(newText) 
            testCorpus.append(newText)
    return testCorpus

def perform_preprocessing_topic_text(comments):
    emoji_dict=emoji_dictionary()
    topicCorpus=[]
    for text in comments:
        try:
            lang = detect(text)
        except:
            lang = ""
        if lang == "en":
            newText = text.strip()
            newText = replace_emojis(newText, emoji_dict)
            topic_text = preprocess_topic_text(newText) 
            topicCorpus.append(topic_text)
    return topicCorpus
    
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8002)

#Uncomment this before running the file and give the uniqueid created 
#when you used the jupyter notebook on your system to push code into the MySQL DB

#runner(29873)