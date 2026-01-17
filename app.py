from flask import Flask, render_template, request, jsonify
import moviesearcher
import parent
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini - Ensure 'GEMINI_API_KEY' is set in Render Environment Variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

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

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    details = data.get('details', [])
    movie_title = data.get('title', 'this movie')
    
    # Culturally aware prompt for Indian households
    prompt = f"""
    Acting as a content advisor for an Indian household, analyze these incidents for '{movie_title}':
    {details}

    Focus heavily on Sexual Content and Nudity as these are major deal-breakers for Indian families.
    Provide a concise 2-3 sentence verdict:
    1. Is there nudity or "awkward" sexual content for drawing-room viewing?
    2. Is the violence stylized action or excessively gory?
    3. Final Verdict: Use "Safe for family viewing" or "Avoid watching with parents/kids".
    """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"summary": response.text})
    except Exception as e:
        return jsonify({"summary": "AI intelligence unavailable at the moment."})

if __name__ == '__main__':
    app.run(debug=True)