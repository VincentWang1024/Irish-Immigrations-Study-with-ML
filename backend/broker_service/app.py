from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, supports_credentials=True)
# CORS(app, resources={r'/*' : {'origins': ['http://localhost:3003']}})
