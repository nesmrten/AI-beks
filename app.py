from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf.csrf import generate_csrf
from config import Config
from sqlalchemy.exc import IntegrityError
import secrets
import string
from forms import RegistrationForm


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Function to create the database automatically on the first run
@app.before_first_request
def create_tables():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(32), nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    def generate_reset_token(self):
        self.token = secrets.token_urlsafe(16)
        self.token_expiration = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.token

    def reset_password(self, password):
        self.password = generate_password_hash(password)
        self.token = None
        self.token_expiration = None
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Log the user in
            session["user_id"] = user.id
        flash('Login successful!') 
        return redirect("/index.html")
    else: 
        flash("Invalid email or password", "error") 
        csrf_token = generate_csrf() 
        return render_template("login.html", csrf_token=csrf_token)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email address is already in use. Please choose a different email address.')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/get', methods=['POST'])
def get_bot_response():
    userText = request.form['msg']
    # Your custom AI logic goes here
    bot_response = "This is the response from your custom AI."
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
