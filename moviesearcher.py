import requests

def search_imdb(movie_name):
    """Fetches search results from IMDb API."""
    url = f"https://v3.sg.media-imdb.com/suggestion/{movie_name[0].lower()}/{movie_name.replace(' ', '%20')}.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        results = []
        if "d" in data:
            for item in data["d"]:
                if "id" in item:
                    results.append({
                        "display": f"{item.get('l', 'Unknown')} ({item.get('y', 'N/A')})",
                        "id": item.get("id")
                    })
        return results
    except Exception:
        return []