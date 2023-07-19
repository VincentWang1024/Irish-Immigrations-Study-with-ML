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
from producer.main import batch_engine

@app.route('/api/comments', methods=['POST'])
def comments():
<<<<<<< HEAD
=======
    print(request.json)
>>>>>>> main
    try:
        _json = request.json
        # if _number and _url and _model_id and request.method == 'POST':
        if 'number' not in _json or 'url' not in _json or 'model_id' not in _json:
                return jsonify({'status': 'error', 'message': 'url, commentcount, jobID, and model_id are required fields'}), 400
        _number = _json['number']
        _url = _json['url']
        _model_id = _json['model_id']
<<<<<<< HEAD
        print(_number, _url, _model_id)
=======
        # print(_number, _url, _model_id)
>>>>>>> main

        job_id = str(uuid.uuid1())
        job_time = datetime.now()

        print("...........request data service......................")
<<<<<<< HEAD
        response = requests.post('http://data_service:8001/comments', json={
=======
        r = requests.post('http://data_service:8001/comments', json={
        # r = requests.post('http://127.0.0.1:8001/comments', json={
>>>>>>> main
            "url": _url,
            "commentcount":_number,
            "jobid": job_id,
            "modelid": _model_id
<<<<<<< HEAD
        })
        print("............data service respond.....................")
        print(f"Status Code: {response.status_code}, Response: {response.json()}")
        save_job(job_id, _url, job_time)
        job_output_polling(job_id)
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'pipeline executed successfully!'}), 200
        elif response.status_code == 500:
=======
        }, timeout=600)
        # breakpoint()
        print(f'print response: {r}')
        print("............data service respond.....................")
        save_job(job_id, _url, _model_id, job_time)
        plain_result = job_output_polling(job_id)
        goemotion_result = goemotion_find(job_id)
        model_result={}

        if r.status_code == 200:
            # Adding the 2 results to the model_result dictionary
            model_result['barchart_data'] = plain_result
            model_result['piechart_data'] = goemotion_result
            # clear slash in json data
            for item in model_result['piechart_data']:
                item["goemotion_result"] = json.loads(item["goemotion_result"])
            respone = jsonify(model_result)
            respone.status_code = 200
            print(respone)
            return respone
        elif r.status_code == 500:
>>>>>>> main
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
    

<<<<<<< HEAD

@app.route('/api/model/result', methods=['POST'])
def model_output():
=======
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
>>>>>>> main
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


<<<<<<< HEAD
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
=======
@app.route('/api/batch', methods=['POST'])
def batch_runner():
    try:
        data = request.json
        topic = data['topic']
        batch_engine(topic)
        response = jsonify(f'topic: [{topic}] has been sent to kafka queue successfully!')
>>>>>>> main
        print(response)
        response.status_code = 200
        return response
    except Exception as e:
<<<<<<< HEAD
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
=======
        showMessage()
        return jsonify(message=str(e), status=500) # added this line


def goemotion_find(job_id):
    try:
        # store result into database
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM goemotion_result_table where job_id=%s"
        cursor.execute(sql, job_id)
        conn.commit()
        resultRows = cursor.fetchall()
        return resultRows
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
>>>>>>> main


def get_result(job_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # try to get model output from DB
    sqlQuery = "SELECT * FROM job_output where job_id=%s"
    cursor.execute(sqlQuery, (job_id,))
    resultRows = cursor.fetchall()
    print("length of result "+str(len(resultRows)))
    return resultRows


<<<<<<< HEAD
def save_job(job_id, _url, job_time):
=======
def save_job(job_id, _url, _model_id, job_time):
>>>>>>> main
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


def job_output_polling(job_id):
    try:
        max_attempts = 20
        attempt = 0
        while attempt < max_attempts:
            resultRows = get_result(job_id)
            if resultRows: 
                print("Result: ", resultRows)
                print("Got data from database!")
                return resultRows
            else:
                print("No result yet. Sleeping...")
                time.sleep(3)
                attempt += 1
        print("Failed to get result after max attempts")
    except Exception as e:
        print(e)

<<<<<<< HEAD
=======
@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response

>>>>>>> main

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)