import json
import secrets
import uuid
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_qrcode import QRcode
from flask_uuid import FlaskUUID
from app import app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_project.db'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

qrcode = QRcode(app)
FlaskUUID(app)



# You can generate a Token from the "Tokens Tab" in the UI
url_base = 'http://192.168.1.5:5002/'

class Qr(db.Model):
    __tablename__ = 'Qr'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100))
    qr_data = db.Column(db.String(255))
    redirect_uri = db.Column(db.String(255))
    name = db.Column(db.String(100))
    visits = db.relationship('Visitor', backref='qr', cascade = 'all, delete-orphan', lazy = 'dynamic')


class Visitor(db.Model):
    __tablename__ = 'Visitors'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(255))
    time = db.Column(db.DateTime())
    uuid = db.Column(db.String(100))
    qr_scanned = db.Column(db.Integer, db.ForeignKey(Qr.uuid) )





@app.route('/hello')
def hello():
    return "hello world"


@app.route('/')
@app.route('/index')
def index():
    #visitors = Visitor.query.all()
    #return render_template('index.html')
    return render_template('index.html', user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr), user_agent=request.user_agent)

@app.route('/view/<uuid:id>')
def view_uuid(id):
    visitors = Visitor.query.filter_by(uuid = str(id))
    return render_template('index.html', visitors=visitors)


@app.route('/view')
def view_campaigns():
    qrs = Qr.query.all()
    return render_template('qr_list.html', qrs=qrs)

@app.route('/<uuid:id>')
def visituuid(id):
    user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent=str(request.user_agent)
    time = datetime.now()

    visitor = Visitor(ip_address=user_ip, user_agent=user_agent, time=time, qr_scanned=str(id), uuid=str(id))
    db.session.add(visitor)
    db.session.commit()
    visitors = Visitor.query.filter_by(uuid = str(id))
    return render_template('index.html', user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr), user_agent=request.user_agent, visitors=visitors)

@app.route('/create', methods = ['POST', 'GET'])
def createqr():

    random_uuid = uuid.uuid4()
    qr_uri = f'{url_base}{random_uuid}'

    if request.method == 'POST':
        #if qr_data:
        #    validate_uri(qr_data)
        print(request.form)
        name=request.form.get('name')
        if name == '':
            name=None
        redirect_uri=request.form.get('redirect_uri')
        this_qr = Qr(uuid=str(random_uuid), qr_data=qr_uri, name=name, redirect_uri=redirect_uri)
        db.session.add(this_qr)
        db.session.commit()
        return redirect(url_for('view_uuid',id = str(random_uuid)))
    else:
        return render_template('create_qr.html', qr_uri=qr_uri, redirect_uri=f'{url_base}view/{random_uuid}')

@app.route('/all')
def all_visits():
    visitors = Visitor.query.all()
    return render_template('all_visits.html', visitors=visitors)

db.create_all()

#app.run()
