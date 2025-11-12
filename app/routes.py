from flask import Flask, render_template, request, redirect, url_for, session
from app import db
from app.models import User


def register_routes(app):

    @app.route('/')
    def home():
        return render_template('index.html')


    @app.route('/about')
    def about():
        return render_template('about.html')


    @app.route('/intake')
    def intake():
        return render_template('intake.html')


    @app.route('/login')
    def login():
        return render_template('login.html')


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            age = request.form.get('age')
            password = request.form.get('password')  

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('register.html', error='E-mailadres bestaat al!')

            new_user = User(name=name, email=email, age=age)
            db.session.add(new_user)
            db.session.commit()

            session['email'] = email
            session['name'] = name

            return redirect(url_for('home'))

        return render_template('register.html')