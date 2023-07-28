import uuid
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from googleapiclient.discovery import build
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import time
import pymysql
from datetime import datetime
from config import mysql

load_dotenv()

# Load environment variables
bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS")
security_protocol = os.getenv("SECURITY_PROTOCOL")
sasl_mechanisms = os.getenv("SASL_MECHANISMS")
sasl_username = os.getenv("SASL_USERNAME")
sasl_password = os.getenv("SASL_PASSWORD")

# Create a Kafka producer configuration
conf = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': security_protocol,
    'sasl.mechanisms': sasl_mechanisms,
    'sasl.username': sasl_username,
    'sasl.password': sasl_password,
}


def error_cb(err):
    """ The error callback is used for generic client errors. These
        errors are generally to be considered informational as the client will
        automatically try to recover from all errors, and no extra action
        is typically required by the application.
        For this example however, we terminate the application if the client
        is unable to connect to any broker (_ALL_BROKERS_DOWN) and on
        authentication errors (_AUTHENTICATION). """

    print("Client error: {}".format(err))
    if err.code() == KafkaError._ALL_BROKERS_DOWN or \
       err.code() == KafkaError._AUTHENTICATION:
        # Any exception raised from this callback will be re-raised from the
        # triggering flush() or poll() call.
        raise KafkaException(err)


def acked(err, msg):
    """Delivery report callback called (from flush()) on successful or failed delivery of the message."""
    if err is not None:
        print('Failed to deliver message: {}'.format(err.str()))
    else:
        print('Produced to: {} [{}] @ {}'.format(msg.topic(), msg.partition(), msg.offset()))


DEVELOPER_KEY = os.getenv('CLIENT_SECRET')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    # Create producer
    p = Producer(**conf)

    # Initialize the page token.
    page_token = None
    while True:
        # to save api quota, add a thread sleep handling
        # time.sleep(10)

        # Call the search.list method to retrieve results matching the specified query term.
        search_response = youtube.search().list(
            q=options.q,
            part='id,snippet',
            maxResults=options.max_results,
            pageToken=page_token  # Add this line to use the page token in the request.
        ).execute()

        videos = []
        urls = []
        channels = []
        playlists = []

        # Add each result to the appropriate list.
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append('%s (%s)' % (search_result['snippet']['title'],
                                           search_result['id']['videoId']))
                url='https://www.youtube.com/watch?v=%s' % search_result['id']['videoId']
                print(f'enque url:{url}')
                urls.append(url)

                job_id = str(uuid.uuid1())
                job_time = datetime.now()

                save_job(job_id, url, '', job_time)
                # producer generate nlp workflow tasks
                p.produce('nlp-workflow', value=f'[{job_id}, {url}]',callback=acked)
                p.poll()
            elif search_result['id']['kind'] == 'youtube#channel':
                channels.append('%s (%s)' % (search_result['snippet']['title'],
                                             search_result['id']['channelId']))
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                              search_result['id']['playlistId']))

        # Output the video URLs.
        # print('Video URLs:\n', '\n'.join(urls), '\n')

        # Update the page token for the next iteration.
        page_token = search_response.get('nextPageToken')
        if not page_token:
            p.flush()
            break  # Exit the loop when there are no more pages.


def save_job(job_id, _url, _model_id, job_time):
    conn=None
    cursor=None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sqlQuery = "INSERT INTO job(id, video_link, model_id, job_time) VALUES(%s, %s, %s, %s)"
        bindData = (job_id, _url, _model_id, job_time)
        cursor.execute(sqlQuery, bindData)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class Options:
    def __init__(self, q, max_results):
        self.q = q
        self.max_results = max_results

def batch_engine(topic):
    options = Options(topic, 50)
    youtube_search(options)

# batch_engine('immigrant ireland')