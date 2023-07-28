# Youtube API Setup (For Windows) 
# pip install virtualenv
# virtualenv yt-comment-fetcher
# yt-comment-fetcher\Scripts\activate
# yt-comment-fetcher\Scripts\pip.exe install google-api-python-client

# Youtube API Setup (For Mac/Linux) 
# pip3 install virtualenv
# virtualenv yt-comment-fetcher
# source yt-comment-fetcher/bin/activate
# yt-comment-fetcher/bin/pip install google-api-python-client

# Other packages
# pip install python-dotenv
# pip install mysql-connector-python
# pip install validators
# pip install Flask

import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime

from googleapiclient.discovery import build
from dotenv import load_dotenv
from apiclient.errors import HttpError
import mysql.connector
import validators
from validators.utils import ValidationFailure
from flask import Flask, request, Response, jsonify
import requests
app = Flask(__name__)

@app.route("/comments", methods=['GET','POST'])
def process_comments():
    try:
        data = request.json
        if 'url' not in data or 'commentcount' not in data or 'jobid' not in data or 'modelid' not in data or 'pps_id' not in data:
            return jsonify({'status': 'error', 'message': 'url, commentcount, jobID, model_id, and pps_id are required fields'}), 400
        url = data['url']
        comment_count = data['commentcount']
        job_id = data['jobid']
        model_id = data['modelid']
        pps_id = data['pps_id']
        if not url:
            raise ValueError("Empty url")
        elif not comment_count:
            raise ValueError("Empty Comment count")
        elif not job_id:
            raise ValueError("Empty job id")
        elif not model_id:
            raise ValueError("Empty model id")
        elif not pps_id:
            raise ValueError("Empty pps_id")

        load_dotenv()
        video_id = get_video_id_from_url(url)
        comments = get_comments(video_id, comment_count)        
        save_comments_to_database(job_id, comments)
        preprocess_url = 'http://preprocess_service:8002/api/preprocess'
        #preprocess_url = 'http://127.0.0.1:8002/api/preprocess'
        median_time = get_median_time_for_comments(comments)
        response = requests.post(preprocess_url, json={'jobID': job_id, 'model_id': model_id, 'pps_id': pps_id, 'median_time': median_time}, timeout=600)
        if response.status_code == 200:
            return Response("Comments OK", status=200)
        else:
            return Response("Future Calls Failed", status=500)

    except KeyError:
        print("Please enter a valid youtube video link......")
    except ValidationFailure:
        print("Invalid URL")
    except mysql.connector.Error as err:
        print("MySQL Error")
        print(err)
    except ValueError as err:
        print(err)
    except HttpError as err:
        print("An HTTP error %d occurred:\n%s" % (err.resp.status, err.content))

def get_video_id_from_url(url):
    validator = validators.url(url)
    if validator:
        youtube_url = urlparse(url)
        video_id = parse_qs(youtube_url.query)['v'][0]
        return video_id
    else:
        raise validator
         
def save_comments_to_database(job_id, comments):
    cnx = mysql.connector.connect(user=os.getenv('MYSQL_ROOT_USERNAME'),
                                       password=os.getenv('MYSQL_ROOT_PASSWORD'),
                                       host=os.getenv('MYSQL_HOST'),
                                       database=os.getenv('MYSQL_DB'))
    add_comment = ("INSERT INTO usercomments "
                   "(jobid, comments, comment_date, job_time) "
                   "VALUES (%s, %s, %s, %s)")
    cursor = cnx.cursor()
    job_time = datetime.now()

    for comment in comments:
        data_comment = (job_id, comment[0], comment[1], job_time)
        cursor.execute(add_comment, data_comment)
    
    cnx.commit()  
    cursor.close()
    cnx.close()

def get_comments(video_id, comment_count, comments = [], pgtoken=""):
    api_key = os.getenv('CLIENT_SECRET')
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.commentThreads().list(
        part = "snippet,replies",
        videoId = video_id,
        pageToken = pgtoken,
        textFormat = "plainText"
        ).execute()

    for item in response["items"]:
        if(len(comments) < comment_count):
            parent_id = item["id"]
            topLevelComment = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            commentDate = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            commentInfo = (topLevelComment, commentDate)
            comments.append(commentInfo)

            replies = youtube.comments().list(
                part="snippet",
                parentId = parent_id,
                textFormat="plainText"
                ).execute()
            
            for reply in replies["items"]:
                if(len(comments) < comment_count):
                    replyComment = reply["snippet"]["textOriginal"]
                    replyDate = reply["snippet"]["publishedAt"]
                    replyInfo = (replyComment, replyDate)
                    comments.append(replyInfo)
                else:
                    return comments
        else:
            return comments

    if "nextPageToken" in response:
        return get_comments(video_id, comment_count, comments, response["nextPageToken"])
    else:
        return comments

def get_median_time_for_comments(comments):
    comment_datetimes = []
    for comment in comments:
        comment_datetimes.append(comment[1])

    comment_timestamps = [datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") for time in comment_datetimes]
    comment_timestamps = sorted(comment_timestamps)
    num_timestamps = len(comment_timestamps)
    if num_timestamps % 2 == 0:
        date1 = comment_timestamps[num_timestamps // 2 - 1]
        date2 = comment_timestamps[num_timestamps // 2]

        if date1 < date2:
            time_diff = date2 - date1
            median_timestamp = date1 + (time_diff // 2)
        else:
            time_diff = date1 - date2
            median_timestamp = date2 + (time_diff // 2)
    else:
        median_timestamp = comment_timestamps[num_timestamps // 2]
    return median_timestamp.__str__()

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8001)