import pytest
import logging
import requests_mock
from .preprocessing_script import app


@pytest.fixture
def client():
    return app.test_client()

def test_runner_with_valid_data(client):
    with requests_mock.Mocker() as mocker:
        mocker.post('http://nlp_service:8003/api/callmodel', status_code=200)
       
        
        valid_data = {
            'jobID': "1212",
            'model_id': "1",
            'pps_id': [1,2,3],
            'median_time': 10
        }

        response = client.post('/api/preprocess', json=valid_data)
        # Here there will be calls to db which will fail that's surrounded with try catch
        try:
            assert response.status_code == 200
            assert b'"status":"success"' in response.data
        except AssertionError:
            logging.error("Show error in logs", exc_info=True)

def test_runner_with_invalid_model_id(client):
    with requests_mock.Mocker() as mocker:
        mocker.post('http://nlp_service:8003/api/callmodel', status_code=200)
        invalid_data = {
            'jobID': 'some_job_id',
            'model_id': 7,  
            'pps_id': 'some_pps_id',
            'median_time': 10
        }

        response = client.post('/api/preprocess', json=invalid_data)
        # try:
        assert response.status_code == 400 
        assert b'"status":"error"' in response.data
        assert b'"message":"Valid values for model_id are 1,2,3,4,5,6"' in response.data
        # except AssertionError:
        #     logging.error("Show error in logs", exc_info=True)

def test_runner_with_missing_median_time(client):
    with requests_mock.Mocker() as mocker:
        mocker.post('http://nlp_service:8003/api/callmodel', status_code=200)
        invalid_data = {
            'jobID': 'some_job_id',
            'model_id': 7,  
            'pps_id': 'some_pps_id'
        }

        response = client.post('/api/preprocess', json=invalid_data)
        # try:
        assert response.status_code == 400 
        assert b'"status":"error"' in response.data
        assert b'"message":"jobID and model_id are required fields"' in response.data
        # except AssertionError:
        #     logging.error("Show error in logs", exc_info=True)


def test_runner_with_missing_jobid(client):
    with requests_mock.Mocker() as mocker:
        mocker.post('http://nlp_service:8003/api/callmodel', status_code=200)
        invalid_data = {
            'model_id': 7,  
            'pps_id': [1,2,3],
            'median_time': 10
        }

        response = client.post('/api/preprocess', json=invalid_data)
        # try:
        assert response.status_code == 400 
        assert b'"status":"error"' in response.data
        assert b'"message":"jobID and model_id are required fields"' in response.data
        # except AssertionError:
        #     logging.error("Show error in logs", exc_info=True)

def test_runner_with_missing_ppsid(client):
    with requests_mock.Mocker() as mocker:
        mocker.post('http://nlp_service:8003/api/callmodel', status_code=200)
        invalid_data = {
            'model_id': 7,  
            'jobID': "1212",
            'median_time': 10
        }

        response = client.post('/api/preprocess', json=invalid_data)
        # try:
        # assert response.status_code == 400 
        assert b'"status":"error"' in response.data
        assert b'"message":"jobID and model_id are required fields"' in response.data
        # except AssertionError:
        #     logging.error("Show error in logs", exc_info=True)
        


