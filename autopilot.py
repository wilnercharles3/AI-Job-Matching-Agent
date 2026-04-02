import os
import requests
import smtplib
from email.mime.text import MIMEText
from google import genai
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, html_content):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_APP_PASSWORD")
    if not sender or not password:
        print("❌ Email credentials missing.")
        return False
    
    msg = MIMEText(html_content, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def run_autopilot():
    print("🚀 Starting AI Job Agent (Verification Mode)...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    contact_email = os.getenv("EMAIL_SENDER")
    client = genai.Client(api_key=api_key)

    # 1. Search
    params = {"engine": "google_jobs", "q": "Strategic Account Executive", "api_key": serp_key, "num": 5}
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        jobs = response.json().get("jobs_results", [])
        
        valid_matches = []
        for job in jobs:
            title, company = job.get("title"), job.get("company_name")
            desc = job.get("description", "")
            
            # --- BROAD FILTER FOR TESTING ---
            criteria = "Any professional role is a match for this test."
            
            prompt = f"Grade this: {title} @ {company}. Req: {criteria}. Desc: {desc}. If match, give 1-sentence summary. If not, start with 'FAIL'."
            res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            
            if not res.text.startswith("FAIL"):
                print(f"✅ Test Match Found: {title}")
                valid_matches.append(f"<h3>{title} @ {company}</h3><p>{res.text}</p><hr>")

        # 2. Dispatch
        if valid_matches:
            print("🎯 Found matches! Dispatching test email...")
            report = "<h2>🌅 Morning Executive Brief (TEST)</h2>" + "".join(valid_matches)
            if send_email(contact_email, "🌅 TEST: Your Executive Job Brief", report):
                print("📧 Email sent successfully.")
        else:
            print("🛡️ No jobs found even with broad filters.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_autopilot()