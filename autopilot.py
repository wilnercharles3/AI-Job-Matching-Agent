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
    print("🚀 Starting Balanced AI Job Agent...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    contact_email = os.getenv("EMAIL_SENDER")
    client = genai.Client(api_key=api_key)

    # 1. Market Search
    params = {
        "engine": "google_jobs",
        "q": "Strategic Account Executive",
        "api_key": serp_key,
        "num": 15 # Scrutinizing more jobs to find the best ones
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
            
            # --- UPDATED FLEXIBLE CRITERIA ---
            # Removed Kenya. Softened Remote to include "Hybrid" or "Remote-First"
            prompt = f"""
            Grade this job: {title} at {company}.
            Target Profile: Strategic Account Executive.
            Preferences: Prefers Remote, but open to strong Hybrid or 'Remote-First' roles.
            Job Description: {desc}
            
            If this is a high-quality professional match, give a 2-sentence summary of the opportunity.
            If it is clearly a bad match (e.g., entry level or strictly on-site in a far city), start with 'FAIL'.
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            
            if not res.text.startswith("FAIL"):
                print(f"✅ Match Found: {title} @ {company}")
                match_html = f"""
                <div style="border-bottom: 1px solid #ddd; padding: 20px; margin-bottom: 10px;">
                    <h3 style="color: #2E86C1; margin-bottom: 5px;">{title} @ {company}</h3>
                    <p style="color: #333; line-height: 1.5;">{res.text}</p>
                    <a href="{link}" style="background-color: #28B463; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block;"><b>View Application</b></a>
                </div>
                """
                valid_matches.append(match_html)
            else:
                print(f"❌ Skipped: {title}")

        # 2. Dispatch
        if valid_matches:
            print(f"🎯 Found {len(valid_matches)} high-quality matches! Sending email...")
            report = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #2C3E50;">🌅 Steve's Morning Executive Brief</h2>
                <p>I've scanned the current market and hand-picked these {len(valid_matches)} roles for you:</p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                {"".join(valid_matches)}
                <br>
                <p style="font-size: 11px; color: #999;"><i>Powered by your AI Job Matching Agent.</i></p>
            </body>
            </html>
            """
            if send_email(contact_email, "🌅 Your 5:00 AM Executive Job Brief", report):
                print("📧 Email sent successfully.")
        else:
            print("🛡️ Scan complete. No matches found with the current filters.")

    except Exception as e:
        print(f"⚠️ Error during autopilot: {e}")

if __name__ == "__main__":
    run_autopilot()