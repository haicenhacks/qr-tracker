from flask import Flask, jsonify, request
import json

from app import app

from datetime import datetime

import secrets
# You can generate a Token from the "Tokens Tab" in the UI



@app.route('/')
@app.route('/index')
def index():
    return f"{request.environ.get('HTTP_X_REAL_IP', request.remote_addr)} - {request.user_agent}"


#app.run()
