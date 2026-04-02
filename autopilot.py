import os
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

def run_autopilot():
    print("🚀 Starting Independent Autopilot Scan...")
    
    # 1. Configuration
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    client = genai.Client(api_key=api_key)

    # 2. Search for Jobs
    print("📡 Searching SerpApi for roles...")
    search_url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": "Strategic Account Executive",
        "api_key": serp_key,
        "num": 10
    }
    
    response = requests.get(search_url, params=params)
    jobs = response.json().get("jobs_results", [])
    
    # 3. Grade with Gemini
    valid_matches = []
    for job in jobs:
        title = job.get("title")
        company = job.get("company_name")
        description = job.get("description", "")
        
        prompt = f"Grade this job: {title} at {company}. Requirements: 100% Remote, Kenya-friendly. Job Desc: {description}. If it matches, give a 2-sentence summary. If not, start with 'FAIL'."
        
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        if not res.text.startswith("FAIL"):
            print(f"✅ Match: {title}")
            valid_matches.append(f"<h3>{title} @ {company}</h3><p>{res.text}</p><hr>")

    # 4. Success?
    if valid_matches:
        print(f"🎯 Found {len(valid_matches)} matches. Sending email...")
        # (Email logic here if keys are set)
    else:
        print("🛡️ No matches found today.")

if __name__ == "__main__":
    run_autopilot()