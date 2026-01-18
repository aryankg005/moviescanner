from flask import Flask, render_template, request, jsonify
import moviesearcher
import parent
import google.generativeai as genai
import os

app = Flask(__name__)

# 1. SETUP GEMINI
# Ensure the key name here matches the Key name in Render Environment Variables exactly
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    # Using flash model for speed and reliability
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("CRITICAL ERROR: GEMINI_API_KEY not found in environment variables.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json.get('query')
        results = moviesearcher.search_imdb(query)
        return jsonify(results)
    except Exception as e:
        print(f"Search Error: {str(e)}")
        return jsonify([])

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        movie_id = data.get('id')
        category = data.get('category')
        severity, details = parent.get_advisory_details(movie_id, category)
        return jsonify({"severity": severity, "details": details})
    except Exception as e:
        print(f"Scraper Error: {str(e)}")
        return jsonify({"severity": "Error", "details": ["Failed to fetch data from IMDb."]})

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    details = data.get('details', [])
    movie_title = data.get('title', 'this movie')
    
    # Prompt specifically tuned for Indian family sensitivities
    prompt = f"""
    Act as a conservative Indian parent content advisor. 
    Analyze these IMDb parental guide incidents for the movie '{movie_title}':
    {details}

    Strictly evaluate if this is safe for a 'Drawing Room' viewing with kids and parents. 
    Focus mostly on Sex, Nudity, and awkward romantic scenes.
    Provide a 2-sentence verdict. 
    Start the response with either 'SAFE FOR FAMILY' or 'AVOID WITH FAMILY'.
    """
    
    try:
        if not GEMINI_KEY:
            return jsonify({"summary": "AI Error: API Key is missing in Render settings."})
            
        response = model.generate_content(prompt)
        
        # Check if Gemini returned a valid response
        if response and response.text:
            return jsonify({"summary": response.text})
        else:
            return jsonify({"summary": "AI was unable to generate a verdict for this specific content."})
            
    except Exception as e:
        # This will print the exact reason (e.g., Expired Key, Wrong Key) in Render Logs
        print(f"DEBUG GEMINI ERROR: {str(e)}")
        return jsonify({"summary": f"AI Intelligence currently unavailable (Error: {str(e)})"})

if __name__ == '__main__':
    # Use port 5000 or the port provided by the environment
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)