import time

import pymysql
from app import app
from config import mysql
from flask import jsonify
from flask import flash, request, Response
import uuid
import json
import requests
from datetime import datetime


@app.route('/api/comments', methods=['POST'])
def comments():
    try:
        _json = request.json
        # if _number and _url and _model_id and request.method == 'POST':
        if 'number' not in _json or 'url' not in _json or 'model_id' not in _json:
                return jsonify({'status': 'error', 'message': 'url, commentcount, jobID, and model_id are required fields'}), 400
        _number = _json['number']
        _url = _json['url']
        _model_id = _json['model_id']
        print(_number, _url, _model_id)

        job_id = str(uuid.uuid1())
        job_time = datetime.now()

        print("...........request data service......................")
        response = requests.post('http://data_service:8001/comments', json={
            "url": _url,
            "commentcount":_number,
            "jobid": job_id,
            "modelid": _model_id
        })
        print("............data service respond.....................")
        print(f"Status Code: {response.status_code}, Response: {response.json()}")
        save_job(job_id, _url, job_time)
        job_output_polling(job_id)
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'pipeline executed successfully!'}), 200
        elif response.status_code == 500:
            return jsonify({'status': 'error', 'message': 'pipeline has something wrong!'}), 500
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else Happened",err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    return jsonify({'status': 'error', 'message': 'core logic not executed!'}), 501
    


@app.route('/api/model/result', methods=['POST'])
def model_output():
    conn = None
    cursor = None
    try:
        _json = request.json
        _result = _json["result"]
        job_id = _json["job_id"]
        print("before result")
        print(_result, job_id)

        # if _result and job_id and request.method == 'POST':
        # store result into database
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # iterate over each result and insert into database
        for label, ratio in _result.items():
            # SQL insert statement
            sql = "INSERT INTO job_output(label, ratio, job_id) VALUES(%s, %s, %s)"
            cursor.execute(sql, (label, ratio, job_id))
        conn.commit()
        return jsonify(message='result added successfully!', status=200)
    except Exception as e:
        print(e)
        return jsonify(message=str(e), status=500) # added this line
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/api/model/find', methods=['GET'])
def model_find():
    try:
        # store result into database
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM model"
        cursor.execute(sql)
        conn.commit()
        modelRows = cursor.fetchall()
        response = jsonify(modelRows)
        print(response)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
        return jsonify(message=str(e), status=500) # added this line
    finally:
        cursor.close()
        conn.close()


@app.route('/api/model/update', methods=['PUT'])
def model_update():
    conn = None
    cursor = None
    try:
        _json = request.json
        _model_id = _json["model_id"]
        _is_enable = _json["enable"]

        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = "UPDATE model SET enable=%s WHERE id=%s"
        bindData = (_is_enable, _model_id,)
        cursor.execute(sql, bindData)
        conn.commit()
        respone = jsonify('model updated successfully!')
        respone.status_code = 200
        return respone
    except Exception as e:
        showMessage()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return jsonify({'status': 'error', 'message': 'model update failure!'}), 500


@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response


def get_result(job_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # try to get model output from DB
    sqlQuery = "SELECT * FROM job_output where job_id=%s"
    cursor.execute(sqlQuery, (job_id,))
    resultRows = cursor.fetchall()
    print("length of result "+str(len(resultRows)))
    return resultRows


def save_job(job_id, _url, job_time):
    conn=None
    cursor=None
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sqlQuery = "INSERT INTO job(id, video_link, job_time) VALUES(%s, %s, %s)"
        bindData = (job_id, _url, job_time)
        cursor.execute(sqlQuery, bindData)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def job_output_polling(job_id):
    try:
        max_attempts = 20
        attempt = 0
        while attempt < max_attempts:
            resultRows = get_result(job_id)
            if resultRows: 
                print("Result: ", resultRows)
                print("Got data from database!")
                return
            else:
                print("No result yet. Sleeping...")
                time.sleep(3)
                attempt += 1
        print("Failed to get result after max attempts")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)