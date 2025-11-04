from flask import Flask, render_template

app = Flask(__name__)

# route = welke URL iemand bezoekt
@app.route('/')
def home():
    # toon index.html
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)