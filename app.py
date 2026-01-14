from flask import Flask, render_template, request, jsonify
import moviesearcher
import parent

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    results = moviesearcher.search_imdb(query)
    return jsonify(results)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    movie_id = data.get('id')
    category = data.get('category')
    severity, details = parent.get_advisory_details(movie_id, category)
    return jsonify({"severity": severity, "details": details})

if __name__ == '__main__':
    app.run(debug=True)