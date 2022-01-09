import json
import secrets
import uuid
import os
from flask import Flask
from secrets import users

from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, Response
from flask_qrcode import QRcode
from flask_uuid import FlaskUUID
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import flask_login


app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_project.db'
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

db = SQLAlchemy(app)

qrcode = QRcode(app)
FlaskUUID(app)
enable_js_fingerprint = False
# url_base is used to set the redirect uri after the unique url is visited
url_base = f"http://{os.environ['URL_BASE']}"


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('username')
    if email not in users:
        return

    user = User()
    user.id = email
    return user


class Qr(db.Model):
    __tablename__ = 'Qr'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100))
    qr_data = db.Column(db.String(255))
    redirect_uri = db.Column(db.String(255))
    name = db.Column(db.String(100))
    visits = db.relationship('Visitor', backref='qr', cascade = 'all, delete-orphan', lazy = 'dynamic')
    created_by = db.Column(db.String(100))


class Visitor(db.Model):
    __tablename__ = 'Visitors'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(255))
    time = db.Column(db.DateTime())
    uuid = db.Column(db.String(100))
    qr_scanned = db.Column(db.String, db.ForeignKey(Qr.uuid) )



@app.route('/hello')
def hello():
    return "hello world"


@app.route('/')
@app.route('/index')
def index():
    #visitors = Visitor.query.all()
    #return render_template('index.html')
    #print(flask_login.current_user.id)
    user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent=str(request.user_agent)
    time = datetime.now()
    return render_template('index.html', user_ip=user_ip, user_agent=user_agent)


@app.route('/delete/<uuid:id>')
def delete_uuid(id):

    if flask_login.current_user.id == 'admin':
        this_qr = Qr.query.filter_by(uuid = str(id) ).one()
        db.session.delete(this_qr)
        db.session.commit()

    else:
        this_qr = Qr.query.filter_by(uuid=str(id), created_by=flask_login.current_user.id).one()
        if this_qr:
            db.session.delete(this_qr)
            db.session.commit()
    return redirect('/view')


@app.route('/view/<uuid:id>')
def view_uuid(id):

    visitors = Visitor.query.filter_by(uuid = str(id))
    for q in Qr.query.all():
        print(q.uuid == str(id), q.uuid, str(id))
    print(str(id))
    this_qr = Qr.query.filter_by(uuid=str(id)).one()


    return render_template('index.html', visitors=visitors, this_qr=this_qr)


@app.route('/view')
def view_campaigns():
    if flask_login.current_user.id == 'admin':
        print("Admin = true")
        qrs = Qr.query.all()
    else:
        qrs = Qr.query.filter_by(created_by=flask_login.current_user.id)
    return render_template('qr_list.html', qrs=qrs)

@app.route('/<uuid:id>/redirect')
def finalredirect(id):
    print(request.cookies.get('width'))
    print(request.cookies.get('height'))
    user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent=str(request.user_agent)
    this_qr = Qr.query.filter_by(uuid=str(id)).one()
    visitors = Visitor.query.filter_by(uuid = str(id))
    if str(id) not in this_qr.redirect_uri:
        return redirect(this_qr.redirect_uri, 302)

    else:
        return render_template('index.html', user_ip=user_ip, user_agent=user_agent, visitors=visitors)


@app.route('/<uuid:id>')
def visituuid(id):
    user_ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent=str(request.user_agent)
    time = datetime.now()

    visitor = Visitor(ip_address=user_ip, user_agent=user_agent, time=time, qr_scanned=str(id), uuid=str(id))
    db.session.add(visitor)
    db.session.commit()
    this_qr = Qr.query.filter_by(uuid=str(id)).one()
    visitors = Visitor.query.filter_by(uuid = str(id))

    # either redirect to the js fingerprinting page, or the redirect uri as defined
    if enable_js_fingerprint:
        return render_template('visit.html', user_ip=user_ip, user_agent=user_agent, visitors=visitors)

    else:
        if str(id) not in this_qr.redirect_uri:
            return redirect(this_qr.redirect_uri, 302)

        else:
            return render_template('index.html', user_ip=user_ip, user_agent=user_agent, visitors=visitors)


@app.route('/<uuid:id>/edit', methods = ['POST', 'GET'])
@flask_login.login_required
def edit_uuid(id):

    this_qr = Qr.query.filter_by(uuid=str(id)).one()
    if request.method == "POST":
        req_keys = request.form.to_dict().keys()
        print("FORM: ",request.form.to_dict())
        if 'name' in req_keys and 'redirect_uri' in req_keys:
            name = request.form.get('name')
            redirect_uri = request.form.get('redirect_uri')

            this_qr.name = name
            if redirect_uri != "":
                this_qr.redirect_uri = redirect_uri
            else:
                redirect_uri = f'{url_base}{url_for("view_uuid", id=id)}'
                this_qr.redirect_uri = redirect_uri
            ret = db.session.commit()
            print(ret)
            flash('Update successful')
            return redirect(url_for('view_uuid',id = str(id)))
        else:
            return Response("Missing form data (name or redirecturi)", status=403)
    else:
        return render_template('create_qr.html', qr_uri=this_qr.qr_data, name=this_qr.name, redirect_uri=this_qr.redirect_uri)


@app.route('/create', methods = ['POST', 'GET'])
@flask_login.login_required
def createqr():
    """ Creates a unique url in the form of <url_base>/<uuid>, and inserts into database."""

    # Generage random uuid
    random_uuid = uuid.uuid4()

    # construct the url to be encoded in the qr code
    qr_uri = f'{url_base}/{random_uuid}'

    # validate form data
    if request.method == 'POST':
        print(request.form)
        req_keys = request.form.to_dict().keys()
        print(request.form.to_dict())
        if "name" not in req_keys:
            return Response("Missing form data (name)", status=403)
        if "redirect_uri" not in req_keys:
            return Response("Missing form data (redirect_uri)", status=403)
        name=request.form.get('name')
        if name == '':
            name=None

        redirect_uri=request.form.get('redirect_uri')

        if redirect_uri == "":
            redirect_uri = f'{url_base}{url_for("view_uuid", id=random_uuid)}'

        # insert into database. QR code generation happens on page load
        this_qr = Qr(uuid=str(random_uuid), qr_data=qr_uri, name=name, redirect_uri=redirect_uri, created_by=flask_login.current_user.id)

        db.session.add(this_qr)
        db.session.commit()

        # if creation is successful, redirect to the stats page
        return redirect(url_for('view_uuid',id = str(random_uuid)))

    else:
        qr_uri = f'{url_base}/<UUID>'
        return render_template('create_qr.html', qr_uri=qr_uri, redirect_uri="", name="")


@app.route('/all')
@flask_login.login_required
def all_visits():
    visitors = Visitor.query.all()
    return render_template('all_visits.html', visitors=visitors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if request.form['password'] == users[username]['password']:
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('index'))

        return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


db.create_all()

#app.run()
