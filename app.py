import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_migrate import Migrate

app = Flask(__name__, static_folder='static')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')

with app.app_context():
    db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('cities', lazy=True))

with app.app_context():
    db.create_all()
    initial_cities = []
    all_users_id = 1 
    for city_name in initial_cities:
        city = City(name=city_name, user_id=all_users_id)
        db.session.add(city)
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        cities = City.query.filter_by(user_id=session['user_id'])

        weather = []

        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=9575836864a4fccdcaca2ca50a4d6d1e'

        for city in cities:
            r = requests.get(url.format(city.name)).json()
            weather_dict = {
                'id': city.id,
                'city' : city.name,
                'temperature' : r['main']['temp'],
                'description' : r['weather'][0]['description'],
                'icon' : r['weather'][0]['icon'],
            }
            weather.append(weather_dict)

        return render_template('weather.html', weather=weather)
    else:
        return redirect(url_for('login'))

@app.route('/add_city', methods=['POST'])
def add_city():
    if request.method == 'POST':
        city = request.form['city']
        user_id = session.get('user_id')
        new_city = City(name=city, user_id=user_id)
        db.session.add(new_city)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_city', methods=['POST'])
def delete_city():
    city_id = request.form.get('city_id')
    if city_id:
        city = City.query.get(city_id)
        db.session.delete(city)
        db.session.commit()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password == confirm_password:
 
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('register.html', error='Email already in use')
            else:

                hashed_password = generate_password_hash(password, method='sha256')
                new_user = User(email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Passwords do not match')
    else:

        return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/update_city', methods=['POST'])
def update_city():
    city_id = request.form.get('city_id')
    new_city_name = request.form.get('new_city_name')

    # Update the city's name in the database
    city = City.query.filter_by(id=city_id).first()
    city.name = new_city_name  # Fix: Assign the new name to city.name, not city.city
    db.session.commit()

    return redirect(url_for('index'))























