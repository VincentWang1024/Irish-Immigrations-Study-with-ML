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

import os
import sys
sys.path.append("..")
import preprocessing_pipeline.preprocessing_script as second_service
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
from apiclient.errors import HttpError
import mysql.connector
import validators
from validators.utils import ValidationFailure


def process_comments(url, comment_count, job_id):
    try:
        if not url:
            raise ValueError("Empty url")
        elif not comment_count:
            raise ValueError("Empty Comment count")
        elif not job_id:
            raise ValueError("Empty job id")
        load_dotenv()
        video_id = get_video_id_from_url(url)
        comments = get_comments(video_id, comment_count)
        save_comments_to_database(job_id, comments)
        second_service.runner(job_id)
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
                   "(jobid, comments, job_time) "
                   "VALUES (%s, %s, %s)")
    cursor = cnx.cursor()
    job_time = datetime.now()

    for comment in comments:
        data_comment = (job_id, comment, job_time)
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
            comments.append(topLevelComment)

            replies = youtube.comments().list(
                part="snippet",
                parentId = parent_id,
                textFormat="plainText"
                ).execute()
            
            for reply in replies["items"]:
                if(len(comments) < comment_count):
                    replyComment = reply["snippet"]["textOriginal"]
                    comments.append(replyComment)

    if "nextPageToken" in response:
        return get_comments(video_id, comment_count, comments, response["nextPageToken"])
    else:
        return comments
process_comments("https://www.youtube.com/watch?v=8LKAFMByFTY",50,'434343')