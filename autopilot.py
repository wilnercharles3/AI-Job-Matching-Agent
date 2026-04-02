import os
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

def run_autopilot():
    print("🚀 Starting Independent Autopilot Scan...")
    
    # 1. Credentials
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    client = genai.Client(api_key=api_key)

    # 2. Search for Jobs (Strategic Account Executive)
    print("📡 Searching for roles...")
    params = {
        "engine": "google_jobs",
        "q": "Strategic Account Executive",
        "api_key": serp_key,
        "num": 10
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        jobs = response.json().get("jobs_results", [])
        
        valid_matches = []
        for job in jobs:
            title = job.get("title")
            company = job.get("company_name")
            desc = job.get("description", "")
            
            # AI Grading logic
            prompt = f"Grade this job: {title} at {company}. Req: 100% Remote, Kenya-friendly. Desc: {desc}. If match, give 2-sentence summary. If not, start with 'FAIL'."
            res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            
            if not res.text.startswith("FAIL"):
                print(f"✅ Match: {title} @ {company}")
                valid_matches.append(f"<h3>{title} @ {company}</h3><p>{res.text}</p><hr>")

        if valid_matches:
            print(f"🎯 Found {len(valid_matches)} matches. Automation complete.")
        else:
            print("🛡️ No elite matches found today.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_autopilot()