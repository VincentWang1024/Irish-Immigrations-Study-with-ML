#!/usr/bin/env python3
import sys
import json
import unittest
import requests

# sys.path.append("../..")
# from main import *
# from .. import main

def test_api_comments():
     data ={
        "url": "https://www.youtube.com/watch?v=CVix78Az6bE",
        "number": 66,
        "model_id": 1
    }
     response = requests.post("http://127.0.0.1:8000/api/comments", json=data, timeout=600)

     assert response.status_code == 200