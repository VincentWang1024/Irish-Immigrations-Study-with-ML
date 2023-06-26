# imports
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
import numpy as np
import re
import pickle
from langdetect import detect
import tensorflow as tf
from pymongo import MongoClient
from datetime import datetime
import random
import mysql.connector
import sys
sys.path.append("..")
import nlp_engine.model_output as third_service



# mise en place
MAX_SEQUENCE_LENGTH=100
def emoji_dictionary():
    emoji_dict = {}
    with open('preprocessing_pipeline/emoji.txt', 'r', encoding='latin-1') as emoji_file:
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
    return ' '.join(filtered_words)
    

# Accessing MySQL
def SQLConnector(jobID):
    connection = mysql.connector.connect(
        user='root',
        password='bbqsauce',
        host='localhost',
        port=3306,
        database='CNNTest'
    )

    cursor = connection.cursor()
    cursor.execute('SELECT `sentence` FROM `word_embeddings` WHERE `hash` = %s;', (jobID,))
    results = cursor.fetchall()
    sentences = [row[0] for row in results]
    return sentences

def generate_embeddings(sentences):
    emoji_dict=emoji_dictionary()
    testCorpus=[]
    for text in sentences:
            try:
                lang = detect(text)
            except:
                lang = ""
            if lang == "en":
                newText = text.strip()
                newText = replace_emojis(newText, emoji_dict)
                newText = preprocess_text(newText)
                testCorpus.append(newText)
                
    with open('preprocessing_pipeline/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
    input_sequences = tokenizer.texts_to_sequences(testCorpus)
    padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(input_sequences, maxlen=MAX_SEQUENCE_LENGTH)
    return padded_sequences
 
def push_mongo(padded_sequences, jobID):
    try:
        client= MongoClient("mongodb://localhost:27017")
        db=client.get_database('Vector_Data')
        collection=db.preprocessed_data
        for row in padded_sequences:
            document = {str(jobID):row.tolist()}
            collection.insert_one(document)
        print("Data Pushed Successfully")
        
    except Exception as e:
        print("Error while inserting data to MongoDB:")
        print(str(e))
   
def runner(jobID):
    sentences = SQLConnector(jobID)
    padded_sequences = generate_embeddings(sentences)
    push_mongo(padded_sequences, jobID)
    third_service.model_runner(jobID)

#Uncomment this before running the file and give the uniqueid created 
#when you used the jupyter notebook on your system to push code into the MySQL DB

#runner(29873)