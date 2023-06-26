import pymysql
from app import app
from config import mysql
from flask import jsonify
from flask import flash, request
import uuid
import requests
from datetime import datetime
from backend.data_service.YTComment import process_comments


@app.route('/model')
def model():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM model_output")
        modelRows = cursor.fetchall()
        response = jsonify(modelRows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/comments', methods=['POST'])
def comments():
    conn = None
    cursor = None
    try:
        _json = request.json
        _number = _json['number']
        _url = _json['url']
        if _number and _url and request.method == 'POST':
            job_id = str(uuid.uuid1())

            # datetime object containing current date and time
            job_time = datetime.now()

            # r = requests.post('http://localhost:5000/data', json={
            # "job_id": job_id,
            # "url": _url
            # })
            # print(f"Status Code: {r.status_code}, Response: {r.json()}")

            # call data service
            print("call service...")
            process_comments(_url, _number, job_id)

            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO job(id, video_link, job_time) VALUES(%s, %s, %s)"
            bindData = (job_id, _url, job_time)
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            response = jsonify('Job added successfully!')
            response.status_code = 200
            return response
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/model/result', methods=['POST'])
def model_output():
    try:
        _json = request.json
        _result = _json['result']
        job_id = _json['job_id']

        # send back to client
        r = requests.post('http://localhost:3000/dashboard/result', json={
            "job_id": job_id,
            "result": _result
        })
        print(f"Status Code: {r.status_code}, Response: {r.json()}")

        # store result into database
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sqlQuery = "INSERT INTO job_output(label, ratio, job_id) VALUES(%s, %s, %s)"

        for each in _result:
            for k, v in each.items():
                bindData = (k, v, job_id)
                cursor.execute(sqlQuery, bindData)
        conn.commit()
        response = jsonify('result added successfully!')
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=True)
