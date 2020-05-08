import json
import os

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = '236874'
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

now = datetime.now()


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if session.get('current_channel') is None:
            session['current_channel'] = '@original'
        with open('users_credentials.txt') as json_file:
            if os.stat('users_credentials.txt').st_size > 0:
                data = json.load(json_file)
                for i in data:
                    if request.form.get('email') in i['email'] and request.form.get('password') not in i['password']:
                        flash('Incorrect Password', 'danger')
                        return render_template('login.html')
                    if request.form.get('email') in i['email'] and request.form.get('password') in i['password']:
                        session['email'] = i['email']
                        session['display_name'] = i['display_name']
                        return redirect(url_for('home', display_name=session['display_name'], channel=session['current_channel']))
        flash('Email not registered', 'danger')
        return render_template('index.html')
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        x = 0
        with open('users_credentials.txt') as json_file:
            if os.stat('users_credentials.txt').st_size > 0:
                data = json.load(json_file)
                for i in data:
                    if request.form.get('email') in i['email']:
                        flash('Email already registered', 'danger')
                        return render_template('sign_up.html')
        email = request.form.get('email')
        display_name = request.form.get('display_name')
        password = request.form.get('password')
        chanel = '@' + request.form.get('channel')
        with open('channels_info.txt')as f:
            if os.stat('channels_info.txt').st_size > 0:
                chn = json.load(f)
                for c in chn:
                    if email in c['email'] and chanel in c['channel']:
                        x = 1
            else:
                data = []
                chn = []
        if x > 0:
            data.append({'email': email, 'display_name': display_name, 'password': password})
            chn.append({'email': email, 'channel': '@original'})
            with open('users_credentials.txt', 'r+')as f:
                f.truncate(0)
                json.dump(data, f)
                f.close()
            with open('channels_info.txt', 'r+')as f:
                f.truncate(0)
                json.dump(chn, f)
                f.close()
        else:
            data.append({'email': email, 'display_name': display_name, 'password': password})
            chn.append({'email': email, 'channel': '@original'})
            chn.append({'email': email, 'channel': chanel})
            with open('channels_info.txt', 'r+')as f:
                f.truncate(0)
                json.dump(chn, f)
                f.close()

            with open('users_credentials.txt', 'r+')as f:
                f.truncate(0)
                json.dump(data, f)
                f.close()
        flash("Well done, now let's get to work!", 'success')
    return render_template('sign_up.html')


@app.route('/home', methods=["POST", "GET"])
def home():
    if request.method == 'GET':
        channel = session['current_channel']
        if channel == '@original':
            original_welcome = 'This channel is for workspace-wide communication and announcements. All members are in this channel'
        else:
            original_welcome = ''
        chn_list = []
        with open('channels_info.txt') as f:
            data = json.load(f)
            for i in data:
                if session['email'] in i['email']:
                    chn_list.append({'new_channel': i['channel']})

    return render_template('home.html', display_name=session['display_name'], channel=channel, chn_list=chn_list,
                            original_welcome=original_welcome)


@app.route('/channel/<string:new_chn>', methods=['GET'])
def channel(new_chn):
    if request.method == 'GET':
        with open('channels_info.txt') as f:
            if os.stat('channels_info.txt').st_size > 0:
                data = json.load(f)
                for i in data:
                    if new_chn in i['channel']:
                        flash('Channel name already taken ', 'danger')
                        return redirect(url_for('home'))
        data.append({'email': session['email'], 'channel': new_chn})
        with open('channels_info.txt', 'r+')as f:
            f.truncate(0)
            json.dump(data, f)
        new_chn = ''
        f.close()
        flash('New channel added with success', 'success')
    return redirect(url_for('home'))


@app.route('/adduser/<string:email>', methods=['GET'])
def adduser(email):
    if request.method == 'GET':
        with open('channels_info.txt')as f:
            if os.stat('channels_info.txt').st_size > 0:
                data = json.load(f)
                for i in data:
                    if email in i['email'] and session['current_channel'] in i['channel']:
                        flash('This person is already a member of this channel', 'danger')
                        return redirect(url_for('home'))
                    if email in i['email'] and session['current_channel'] == '@original':
                        flash('This person is already a member of this channel', 'danger')
                        return redirect(url_for('home'))
        data.append({'email': email, 'channel': session['current_channel']})
        with open('channels_info.txt', 'r+')as f:
            f.truncate(0)
            json.dump(data, f)
        f.close()
        flash('Contact added with success', 'success')
    return redirect(url_for('home'))


@app.route('/switch_channel/<string:xyz>', methods=['GET'])
def switch_channel(xyz):
    session['current_channel'] = xyz
    return redirect(url_for('home'))


@socketio.on('submit messages')
def handlemessage(msg):
    new_msg = msg['new_msg']
    if session['display_name']:
        display_name = session['display_name']
    local = now.strftime('%d-%m'' ''%H:%M')
    emit('announce message', {'new_msg': new_msg, 'display_name': display_name, 'local': local,
                              'channel': session['current_channel']},broadcast=True)


@socketio.on('flask_bridge')
def requeriments(valor, path):
    destination = path+'/'+valor
    emit('redirect', {'destination': destination})


@app.route('/terms', methods=['GET'])
def terms():
    return render_template('terms.html')

# app.run(debug=True)

socketio.run(app, debug=True)
