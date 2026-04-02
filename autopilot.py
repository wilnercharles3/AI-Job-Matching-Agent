import os
import requests
import smtplib
from email.mime.text import MIMEText
from google import genai
from dotenv import load_dotenv

load_dotenv()

# --- USER CONTROL PANEL ---
# Set this to True if you ONLY want Strategic/High-level roles.
# Set this to False to see both Strategic and Standard AE roles.
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
            title, company = job.get("title"), job.get("company_name")
            desc = job.get("description", "")
            link = job.get("related_links", [{}])[0].get("link", "#")
            
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
                # --- FILTER LOGIC ---
                is_strategic = "[STRATEGIC]" in ai_text
                
                # If the user wants ONLY strategic, skip the standard ones
                if ONLY_STRATEGIC and not is_strategic:
                    print(f"⏭️ Filtering out standard role: {title}")
                    continue
                
                print(f"✅ Match Found: {title}")
                color = "#2E86C1" if is_strategic else "#566573"
                match_html = f"""
                <div style="border-bottom: 1px solid #ddd; padding: 15px; margin-bottom: 10px;">
                    <h3 style="color: {color}; margin-top: 0;">{ai_text[:12]} {title} @ {company}</h3>
                    <p style="color: #444;">{ai_text}</p>
                    <a href="{link}" style="color: #1A73E8; font-weight: bold;">View Opportunity →</a>
                </div>
                """
                valid_matches.append(match_html)

        if valid_matches:
            print(f"🎯 Sending {len(valid_matches)} matches...")
            header = "Strict Strategic Brief" if ONLY_STRATEGIC else "Executive Job Brief"
            report = f"<html><body><h2>🌅 {header}</h2>{''.join(valid_matches)}</body></html>"
            send_email(contact_email, f"🌅 {header}", report)
        else:
            print("🛡️ No matches found for current filter settings.")

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_autopilot()