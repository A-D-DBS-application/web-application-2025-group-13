from app.routes import app


from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
@app.route('/register')
def register():
    return render_template('register.html')

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


if __name__ == '__main__':
    app.run(debug=True)