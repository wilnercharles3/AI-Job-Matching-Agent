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
        # Using standard Gmail SMTP port
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def run_autopilot():
    print("🚀 Starting Balanced AI Job Agent...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    contact_email = os.getenv("EMAIL_SENDER")
    client = genai.Client(api_key=api_key)

    # 1. Search for Roles
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
            link = job.get("related_links", [{}])[0].get("link", "#")
            
            # --- BALANCED CRITERIA ---
            prompt = f"""
            Grade this job: {title} at {company}.
            Target: Strategic Account Executive.
            Preferences: Remote-First or Hybrid. Professional, high-level roles only.
            Job Description: {desc}
            
            If it's a strong match, provide a 2-sentence summary.
            If it's a bad match (entry level, retail, or strictly on-site), start with 'FAIL'.
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            
            if not res.text.startswith("FAIL"):
                print(f"✅ Match: {title} @ {company}")
                match_html = f"""
                <div style="border-bottom: 1px solid #ddd; padding: 15px;">
                    <h3 style="color: #2E86C1;">{title} @ {company}</h3>
                    <p>{res.text}</p>
                    <a href="{link}" style="color: green;"><b>View Job</b></a>
                </div>
                """
                valid_matches.append(match_html)
            else:
                print(f"❌ Skipped: {title}")

        # 2. Dispatch
        if valid_matches:
            print(f"🎯 Found {len(valid_matches)} matches! Sending email...")
            report = "<h2>🌅 Morning Executive Brief</h2>" + "".join(valid_matches)
            if send_email(contact_email, "🌅 Your 5:00 AM Executive Job Brief", report):
                print("📧 Email sent successfully.")
        else:
            print("🛡️ Scan complete. No matches found today.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_autopilot()