import requests
from bs4 import BeautifulSoup
import time

def get_advisory_details(movie_id, category_type):
    clean_id = movie_id.strip('/')
    url = f"https://www.imdb.com/title/{clean_id}/parentalguide"
    
    category_map = {"nudity": "advisory-nudity", "violence": "advisory-violence"}
    heading_map = {"nudity": "Sex & Nudity", "violence": "Violence & Gore"}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        time.sleep(1) # Be respectful to avoid blocks
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try fallbacks: ID -> test-id -> Text Heading
        section = soup.find("section", id=category_map[category_type])
        if not section:
            section = soup.find("section", attrs={"data-testid": f"section-{category_map[category_type]}"})
        if not section:
            heading = soup.find(lambda tag: tag.name in ["h2", "h3", "h4"] and heading_map[category_type].lower() in tag.get_text().lower())
            if heading: section = heading.find_parent("section")

        if not section:
            return "Unknown", ["Category section not found on page."]

        # Extract Severity
        severity = "Unknown"
        for sel in ["span.ipc-chip__text", "div[class*='severity']"]:
            tag = section.select_one(sel)
            if tag and tag.get_text(strip=True).lower() in ["none", "mild", "moderate", "severe"]:
                severity = tag.get_text(strip=True)
                break

        # Extract Descriptions
        results = []
        items = section.select("div.ipc-html-content-inner-div")
        for item in items:
            text = item.get_text(strip=True)
            # Filter noise and vote counts
            if len(text) > 15 and "relevant" not in text.lower() and heading_map[category_type].lower() not in text.lower():
                if " of " in text and " found this" in text:
                    text = text.split(" of ")[0].strip()
                results.append(text)

        return severity, results
    except Exception as e:
        return "Error", [str(e)]