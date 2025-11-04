from flask import Flask, render_template

app = Flask(__name__)

# route = welke URL iemand bezoekt
@app.route('/')
def home():
    # toon index.html
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)