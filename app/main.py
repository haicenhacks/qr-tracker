import json
import secrets
import uuid
from flask import Flask, jsonify, request, render_template
from flask_qrcode import QRcode
from flask_uuid import FlaskUUID
from app import app
from datetime import datetime


qrcode = QRcode(app)
FlaskUUID(app)



# You can generate a Token from the "Tokens Tab" in the UI
url_base = 'http://192.168.1.5:5002/'

@app.route('/hello')
def hello():
    return "hello world"


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr), user_agent=request.user_agent)

@app.route('/<uuid:id>')
def visituuid(id):
    return render_template('index.html', user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr), user_agent=request.user_agent)

@app.route('/create')
def createqr():
    random_uuid = uuid.uuid4()
    qr_data = f'{url_base}{random_uuid}'
    return render_template('create_qr.html', qr_data=qr_data)



#app.run()
