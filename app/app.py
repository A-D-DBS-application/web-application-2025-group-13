from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)

# route = welke URL iemand bezoekt
@app.route('/')
def home():
    # toon index.html
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/intake')
def intake():
    return render_template('intake.html')

if __name__ == '__main__':
    app.run(debug=True)