import os
from app import get_live_jobs, grade_job_with_ai, send_email
from dotenv import load_dotenv

load_dotenv()

def run_daily_scan():
    print("🚀 Autopilot: Starting Daily Executive Scan...")
    
    # 1. Define Steve's core settings (You can eventually pull these from Supabase)
    target_title = "Strategic Account Executive"
    dealbreakers = "100% Remote, Must allow work from Kenya, No micromanagement."
    industry_keywords = "B2B Sales, SaaS, Hospitality"
    target_ote = 250000
    contact_email = os.getenv("EMAIL_SENDER") # Sends to himself by default

    # 2. Scrape 20 jobs
    raw_jobs = get_live_jobs(target_title, limit=20)
    valid_matches = []

    # 3. Grade them
    for job in raw_jobs:
        res = grade_job_with_ai(job, dealbreakers, target_ote, industry_keywords)
        if res and not res.startswith("FAIL"):
            link = job.get('apply_options', [{}])[0].get('link', '#')
            valid_matches.append(f"<h3>{job['title']} @ {job['company_name']}</h3>{res}<br><a href='{link}'>Apply Now</a><hr>")

    # 4. Send Email only if winners are found
    if valid_matches:
        print(f"🎯 Found {len(valid_matches)} elite matches! Sending email...")
        html_report = "".join(valid_matches)
        send_email(contact_email, "🌅 Your Daily Executive Job Brief", html_report)
    else:
        print("🛡️ No jobs passed the 5-star filter today. Keeping the inbox clean.")

if __name__ == "__main__":
    run_daily_scan()