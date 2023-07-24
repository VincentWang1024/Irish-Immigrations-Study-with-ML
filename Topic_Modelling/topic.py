import logging
from flask import Flask, request, jsonify
from bertopic import BERTopic
app = Flask(__name__)

@app.route("/predictTopic", methods=["POST"])
def model():
    if request.method=="POST":
        try:
            json_data = request.get_json()
            topicCorpus=json_data["topic_corpus"]
            if topicCorpus is None or len(topicCorpus)==0:    
                return jsonify({'status': 'error', 'message': 'topic_corpus not found in request'}), 400
            topics_list=topic_detection(topicCorpus) 
            return jsonify(topics_list), 200
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return jsonify({'error': str(e)})


def topic_detection(topicCorpus):
    topics_list = []
    topic_model = BERTopic.load("Bertopic")
    topics, probs = topic_model.transform(topicCorpus)
    data=topic_model.get_topics()
    for topic_id, topic_words in data.items():
        if 0 <= topic_id <= 4:
            top_words_list = []
            for word, probability in topic_words[:5]:
                word_data = {'value': word, 'count': round(probability * 100, 2)}
                top_words_list.append(word_data)
            topic_data = {'id': topic_id, 'name': f'Topic {topic_id + 1}', 'words': top_words_list}
            topics_list.append(topic_data)
    return topics_list


if __name__== "__main__":
    app.run(debug=True,host='0.0.0.0', port=8005)