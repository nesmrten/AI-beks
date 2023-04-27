from flask import Flask, render_template, request, jsonify
from forms import RegistrationForm, LoginForm
from werkzeug.utils import secure_filename
from chatbot import Chatbot
import sqlite3
import json
import logging.config
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

with open('config.json', 'r') as f:
    config = json.load(f)

logging.config.dictConfig(config['logging'])


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        message = request.form['message']
        chatbot = Chatbot(config['model_path'])
        response = chatbot.get_response(message)

        if response.startswith('http'):
            # web scraping
            pass

        language = 'en'
        myobj = gTTS(text=response, lang=language, slow=False)
        myobj.save("response.mp3")

        return jsonify({'response': response})

    return render_template('chat.html', title='Chat')


@app.route('/get_audio', methods=['GET', 'POST'])
def get_audio():
    if request.method == 'POST':
        f = request.files['audio_data']
        filename = secure_filename(f.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(filepath)
        conn = sqlite3.connect(config['database_url'])
        c = conn.cursor()
        c.execute("INSERT INTO recordings (filepath) VALUES (?)", (filepath,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    return render_template('audio.html')


@app.route('/play_recording/<int:id>')
def play_recording(id):
    conn = sqlite3.connect(config['database_url'])
    c = conn.cursor()
    c.execute("SELECT filepath FROM recordings WHERE id=?", (id,))
    filepath = c.fetchone()[0]
    conn.close()
    playsound(filepath)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=config['debug'], port=config['port'])
