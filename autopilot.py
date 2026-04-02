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
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() 
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def run_autopilot():
    print("🚀 Starting Flexible AI Job Agent...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    contact_email = os.getenv("EMAIL_SENDER")
    client = genai.Client(api_key=api_key)

    params = {
        "engine": "google_jobs",
        "q": "Strategic Account Executive",
        "api_key": serp_key,
        "num": 15 
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
            
            prompt = f"""
            Analyze this job: {title} at {company}.
            Goal: Identify roles for an experienced Sales Executive.
            1. Priority: Strategic, Senior, or Enterprise levels.
            2. Secondary: Standard Account Executive roles (Mid-market, etc).
            3. Preference: Remote or Hybrid.
            Job Description: {desc}
            If this is a professional sales role, provide a 2-sentence summary. 
            Label it as [STRATEGIC] if it's a high-level role, or [PROFESSIONAL] if it's a standard AE role.
            If it is clearly entry-level, retail, or unrelated, start with 'FAIL'.
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            
            if not res.text.startswith("FAIL"):
                print(f"✅ Match: {title} @ {company}")
                match_html = f"""
                <div style="border-bottom: 1px solid #ddd; padding: 15px; margin-bottom: 10px;">
                    <h3 style="margin-top: 0;">{title} @ {company}</h3>
                    <p style="color: #444; line-height: 1.4;">{res.text.strip()}</p>
                    <a href="{link}" style="color: #1A73E8; text-decoration: none; font-weight: bold;">View Opportunity →</a>
                </div>
                """
                valid_matches.append(match_html)
            else:
                print(f"❌ Skipped: {title}")

        if valid_matches:
            print(f"🎯 Found {len(valid_matches)} matches! Sending email...")
            report = f"<html><body style='font-family: sans-serif; color: #333;'><h2>🌅 Morning Executive Brief</h2><p>I found {len(valid_matches)} roles for you:</p><hr>{''.join(valid_matches)}</body></html>"
            if send_email(contact_email, "🌅 Your 5:00 AM Executive Job Brief", report):
                print("📧 Email sent successfully.")
        else:
            print("🛡️ Scan complete. No matches found today.")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_autopilot()
