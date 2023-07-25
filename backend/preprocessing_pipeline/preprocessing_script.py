import os
import re
import pickle
from enum import Enum, unique

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

from langdetect import detect
import tensorflow as tf
from pymongo import MongoClient
import mysql.connector
from flask import Flask
from flask import request, jsonify
import requests
app = Flask(__name__)

MAX_SEQUENCE_LENGTH = 100

@unique
class Preprocessing(Enum):
    STEMMING = 1
    LEMMATIZE = 2
    STOPWORD = 3
    EXPANDED = 4
    EMOJI = 5
    MISC = 6

@app.route("/api/preprocess", methods=['POST'])
def runner():
    data = request.json
    if 'jobID' not in data or 'model_id' not in data or 'pps_id' not in data:
        return jsonify({'status': 'error', 'message': 'jobID, model_id, and pps_id are required fields'}), 400
    jobID = data.get('jobID')
    modelID = data.get('model_id')
    pps_id = data.get('pps_id')
    if modelID not in [1, 2, 3]:
        return jsonify({'status': 'error', 'message': 'Valid values for model_id are 1,2,3'}), 400
    try:
        comments = get_comments_from_db(jobID)
        if modelID == 1 or modelID == 2:
            padded_sequences = generate_embeddings(comments, pps_id)
            push_mongo(padded_sequences, jobID)

        testCorpus = perform_preprocessing(comments, pps_id)
        add_corpus_to_db(testCorpus, jobID)
        topicCorpus = perform_preprocessing_topic_text(comments) 
        add_topicCorpus_to_db(topicCorpus, jobID)
        model_runner_url = 'http://nlp_service:8003/api/callmodel'
        #model_runner_url = 'http://localhost:8003/api/callmodel'
        response = requests.post(model_runner_url, json={'jobID': jobID, 'model_id': modelID})
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
    
def default_preprocess_text(text):  
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r'@\w+\s*', '', text)
    return text 

def preprocess_topic_text(text):  
    text = default_preprocess_text(text)
    text = perform_lemmatization(text)
    text = perform_stopwords_removal(text)
    return text

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

def generate_embeddings(comments, pps_id):            
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    testCorpus = perform_preprocessing(comments, pps_id)
    input_sequences = tokenizer.texts_to_sequences(testCorpus)
    padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(input_sequences, maxlen=MAX_SEQUENCE_LENGTH)
    return padded_sequences
 
def push_mongo(padded_sequences, jobID):
    try:
        CONNECTION_STRING = os.getenv('MONGO_URI')
        client = MongoClient(CONNECTION_STRING)
        db = client.get_database('Vector_Data')
        collection = db.preprocessed_data
        for row in padded_sequences:
            document = {str(jobID):row.tolist()}
            collection.insert_one(document)
        print("Data Pushed Successfully To MongoDB")
    except Exception as e:
        print("Error while inserting data to MongoDB:")
        print(str(e))

def perform_preprocessing(comments,pps_id):
    emoji_dict = emoji_dictionary()
    testCorpus = []
    for text in comments:
        try:
            lang = detect(text)
        except:
            lang = ""
        if lang == "en":
            newText = text.strip()
            newText = replace_emojis(newText, emoji_dict)
            newText = default_preprocess_text(newText) 

            for id in pps_id:
                match Preprocessing(id):
                    case Preprocessing.STEMMING:
                        newText = perform_stemming(newText)
                    case Preprocessing.LEMMATIZE:
                        newText = perform_lemmatization(newText)
                    case Preprocessing.STOPWORD:
                        newText = perform_stopwords_removal(newText)
                    case Preprocessing.EXPANDED:
                        newText = perform_preprocessing_on_expanded_text(newText)
                    case Preprocessing.EMOJI:
                        newText = perform_emoji_preprocessing(newText)
                    case Preprocessing.MISC:
                        newText = perform_additional_preprocessing(newText)
            testCorpus.append(newText)
    return testCorpus

def perform_preprocessing_topic_text(comments):
    emoji_dict = emoji_dictionary()
    topicCorpus = []
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

def perform_preprocessing_on_abbv(text):
    text = re.sub(r"lmao", "laughing my ass off", text)  
    text = re.sub(r"amirite", "am i right", text)
    text = re.sub(r"\b(tho)\b", "though", text)
    text = re.sub(r"\b(ikr)\b", "i know right", text)
    text = re.sub(r"\b(ya|u)\b", "you", text)
    text = re.sub(r"\b(eu)\b", "europe", text)
    text = re.sub(r"\b(da)\b", "the", text)
    text = re.sub(r"\b(dat)\b", "that", text)
    text = re.sub(r"\b(dats)\b", "that is", text)
    text = re.sub(r"\b(cuz)\b", "because", text)
    text = re.sub(r"\b(fkn)\b", "fucking", text)
    text = re.sub(r"\b(tbh)\b", "to be honest", text)
    text = re.sub(r"\b(tbf)\b", "to be fair", text)
    text = re.sub(r"faux pas", "mistake", text)
    text = re.sub(r"\b(btw)\b", "by the way", text)
    text = re.sub(r"\b(bs)\b", "bullshit", text)
    text = re.sub(r"\b(kinda)\b", "kind of", text)
    text = re.sub(r"\b(bruh)\b", "bro", text)
    text = re.sub(r"\b(w/e)\b", "whatever", text)
    text = re.sub(r"\b(w/)\b", "with", text)
    text = re.sub(r"\b(w/o)\b", "without", text)
    text = re.sub(r"\b(doj)\b", "department of justice", text)
    text = re.sub(r"\b(ofc)\b", "of course", text)
    text = re.sub(r"\b(the us)\b", "usa", text)
    text = re.sub(r"\b(gf)\b", "girlfriend", text)
    text = re.sub(r"\b(hr)\b", "human resources", text)
    text = re.sub(r"\b(mh)\b", "mental health", text)
    text = re.sub(r"\b(idk)\b", "i do not know", text)
    text = re.sub(r"\b(gotcha)\b", "i got you", text)
    return text

def perform_additional_preprocessing(text):
  text = re.sub(r"h a m b e r d e r s", "hamberders", text)
  text = re.sub(r"b e n", "ben", text)
  text = re.sub(r"s a t i r e", "satire", text)
  text = re.sub(r"y i k e s", "yikes", text)
  text = re.sub(r"s p o i l e r", "spoiler", text)
  text = re.sub(r"thankyou", "thank you", text)
  text = re.sub(r"a^r^o^o^o^o^o^o^o^n^d", "around", text)

  text = re.sub(r"\b([.]{3,})"," dots ", text)
  text = re.sub(r"[^A-Za-z!?_]+"," ", text)
  text = re.sub(r"\b([s])\b *","", text)
  text = re.sub(r" +"," ", text)
  text = text.strip()
  return text

def perform_emoji_preprocessing(text):
  text = re.sub(r"<3", " love ", text)
  text = re.sub(r"xd", " smiling_face_with_open_mouth_and_tightly_closed_eyes ", text)
  text = re.sub(r":\)", " smiling_face ", text)
  text = re.sub(r"^_^", " smiling_face ", text)
  text = re.sub(r"\*_\*", " star_struck ", text)
  text = re.sub(r":\(", " frowning_face ", text)
  text = re.sub(r":\^\(", " frowning_face ", text)
  text = re.sub(r";\(", " frowning_face ", text)
  text = re.sub(r":\/",  " confused_face", text)
  text = re.sub(r";\)",  " wink", text)
  text = re.sub(r">__<",  " unamused ", text)
  text = re.sub(r"\b([xo]+x*)\b", " xoxo ", text)
  text = re.sub(r"\b(n+a+h+)\b", "no", text)
  return text

def perform_preprocessing_on_expanded_text(text):
  text = re.sub(r"\b(j+e{2,}z+e*)\b", "jeez", text)
  text = re.sub(r"\b(co+l+)\b", "cool", text)
  text = re.sub(r"\b(g+o+a+l+)\b", "goal", text)
  text = re.sub(r"\b(s+h+i+t+)\b", "shit", text)
  text = re.sub(r"\b(o+m+g+)\b", "omg", text)
  text = re.sub(r"\b(w+t+f+)\b", "wtf", text)
  text = re.sub(r"\b(w+h+a+t+)\b", "what", text)
  text = re.sub(r"\b(y+e+y+|y+a+y+|y+e+a+h+)\b", "yeah", text)
  text = re.sub(r"\b(w+o+w+)\b", "wow", text)
  text = re.sub(r"\b(w+h+y+)\b", "why", text)
  text = re.sub(r"\b(s+o+)\b", "so", text)
  text = re.sub(r"\b(f)\b", "fuck", text)
  text = re.sub(r"\b(w+h+o+p+s+)\b", "whoops", text)
  text = re.sub(r"\b(y+e+p+)\b", "yes", text)
  text = re.sub(r"\b(a*ha+h[ha]*|a*ha +h[ha]*)\b", "haha", text)
  text = re.sub(r"\b(o?l+o+l+[ol]*)\b", "lol", text)
  text = re.sub(r"\b(o*ho+h[ho]*|o*ho +h[ho]*)\b", "ohoh", text)
  text = re.sub(r"\b(o+h+)\b", "oh", text)
  text = re.sub(r"\b(a+h+)\b", "ah", text)
  text = re.sub(r"\b(u+h+)\b", "uh", text)
  return text

def perform_stemming(text):
    words = word_tokenize(text)
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    filtered_text = ' '.join(words)
    return filtered_text

def perform_lemmatization(text):
    words = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    tagged = pos_tag(words)
    words = [lemmatizer.lemmatize(word, pos=get_wordnet_pos(pos)) if get_wordnet_pos(pos) else word for word, pos in tagged]
    filtered_text = ' '.join(words)
    return filtered_text

def perform_stopwords_removal(text):
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    filtered_text = ' '.join(filtered_words)
    return filtered_text

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8002)