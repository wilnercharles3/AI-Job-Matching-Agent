import os
import requests
import smtplib
from email.mime.text import MIMEText
from google import genai
from dotenv import load_dotenv

load_dotenv()

# --- USER CONTROL PANEL ---
# Set to True to ONLY send Strategic/High-level roles.
# Set to False to include all professional Account Executive roles.
ONLY_STRATEGIC = False 
# --------------------------

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
        # Port 587 with STARTTLS is the most reliable for GitHub Actions
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() 
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def run_autopilot():
    print(f"🚀 Starting AI Job Agent (Strict Filter: {ONLY_STRATEGIC})...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    serp_key = os.getenv("SERPAPI_KEY")
    contact_email = os.getenv("EMAIL_SENDER")
    client = genai.Client(api_key=api_key)

    # Search for Strategic Account Executive roles
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
            
            # AI Grading Logic
            prompt = f"""
            Analyze this job: {title} at {company}.
            1. Label as [STRATEGIC] if it is a Senior, Enterprise, or Strategic level role.
            2. Label as [PROFESSIONAL] if it is a standard Account Executive role.
            3. Preference: Remote or Hybrid.
            Job Description: {desc}
            
            If this fits either category, give a 2-sentence summary. If not, start with 'FAIL'.
            """
            
            res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            ai_text = res.text.strip()

            if not ai_text.startswith("FAIL"):
                is_strategic = "[STRATEGIC]" in ai_text
                
                # Apply the user toggle
                if ONLY_STRATEGIC and not is_strategic:
                    print(f"⏭️ Filtering out standard role: {title}")
                    continue
                
                # Rating and Visuals
                stars = "⭐⭐⭐⭐⭐" if is_strategic else "⭐⭐⭐"
                color = "#2E86C1" if is_strategic else "#566573"
                
                print(f"✅ Match Found: {title} @ {company}")
                match_html = f"""
                <div style="border-bottom: 1px solid #ddd; padding: 15px; margin-bottom: 10px;">
                    <p style="margin: 0; font-size: 12px; color: #888;">{stars}</p>
                    <h3 style="color: {color}; margin-top: 5px;">{title} @ {company}</h3>
                    <p style="color: #444; line-height: 1.5;">{ai_text}</p>
                    <a href="{link}" style="color: #1A73E8; font-weight: bold; text-decoration: none;">View Opportunity →</a>
                </div>
                """
                valid_matches.append(match_html)

        if valid_matches:
            print(f"🎯 Found {len(valid_matches)} matches! Sending email...")
            header_text = "Strict Strategic Brief" if ONLY_STRATEGIC else "Executive Job Brief"
            report = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2C3E50;">🌅 {header_text}</h2>
                <p>I found {len(valid_matches)} roles for you this morning:</p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                {"".join(valid_matches)}
                <p style="font-size: 11px; color: #999; margin-top: 20px;">Powered by your AI Job Agent</p>
            </body>
            </html>
            """
            if send_email(contact_email, f"🌅 {header_text}", report):
                print("📧 Email sent successfully.")
        else:
            print("🛡️ Scan complete. No matches found for current filter settings.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_autopilot()
