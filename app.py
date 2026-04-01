import streamlit as st
import os
import time
import smtplib
import requests
from email.mime.text import MIMEText
from dotenv import load_dotenv
from supabase import create_client
from google import genai

# --- PRO UPGRADE: PREMIUM PAGE LAYOUT ---
st.set_page_config(page_title="Steve's AI Agent", page_icon="👔", layout="centered")

# --- DATABASE, EMAIL & API SETUP ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Supabase
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

# Initialize Gemini AI
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    ai_client = None

# --- PHASE 2: LIVE ENGINES ---
def get_live_jobs(query):
    """Scrapes live remote jobs using SerpApi"""
    if not SERPAPI_KEY: return []
    safe_query = query.replace(" ", "+") + "+Remote"
    url = f"https://serpapi.com/search.json?engine=google_jobs&q={safe_query}&hl=en&api_key={SERPAPI_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("jobs_results", [])[:5] 
    except Exception as e:
        print(f"Scraper Error: {e}")
        return []

def grade_job_with_ai(job, dealbreakers, target_ote, industry_keywords):
    """Hands the job to Gemini to create an Executive Rubric and Keyword Match"""
    if not ai_client: return None
    
    title = job.get('title', 'Unknown Title')
    company = job.get('company_name', 'Unknown Company')
    desc = job.get('description', '')
    
    prompt = f"""
    You are an executive sales headhunter protecting your client's time. 
    Review this job description against these strict requirements:
    - Dealbreakers: {dealbreakers}
    - Target OTE: ${target_ote}
    - Target Industry Keywords: {industry_keywords}

    Job Title: {title}
    Company: {company}
    Description: {desc[:2500]}

    First, decide if this job is a 4 or 5-star overall match. If it is 1, 2, or 3 stars (e.g., micromanagement, low pay, fake remote), strictly return ONLY the word "FAIL".
    
    If it passes, return an Executive Scorecard EXACTLY in this format using a strict 1 to 5 scale:
    
    * **Overall AI Rating:** [Insert 4 or 5 Stars]
    * **Company Intel:** [1 brief sentence summarizing what the company actually does/sells]
    
    **📊 Executive Rubric**
    * 💰 **Compensation ([Score]/5):** [1 sentence explaining base/OTE visibility]
    * 🌍 **Autonomy & Timezone ([Score]/5):** [1 sentence explaining if it's true remote/async or has limits]
    * 🤝 **Sales Support & Role ([Score]/5):** [1 sentence on if they have BDR support or if it's full-cycle]
    
    **🎯 Keyword Matches**
    * [Identify which of the specific Target Industry Keywords were found in the text, and briefly how they are used. If none, say "No specific target keywords explicitly mentioned."]
    """
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        if text == "FAIL" or "FAIL" in text:
            return None
        return text
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def send_confirmation_email(to_email, target_jobs, dealbreakers, job_matches):
    """Sends an automated HTML email via Gmail SMTP"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2E86C1;">🤖 AI Job Bot: Executive Scan Complete</h2>
    <p>Hey Steve,</p>
    <p>Your AI Job Bot is active and scanning.</p>
    <p><b>Target Roles:</b> {target_jobs}</p>
    <hr>
    <p>The engine scanned the global boards, filtered out the micromanagers, and generated your custom rubrics. Here are your live, AI-vetted matches:</p>
    <br>
    {job_matches}
    <br>
    <hr>
    <p><i>- Your Personal AI Agent</i></p>
    </body>
    </html>
    """
    
    msg = MIMEText(email_body, 'html')
    msg['Subject'] = "🤖 AI Job Bot: Live Executive Rubrics Found!"
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# --- UI: SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Alert Settings")
contact_email = st.sidebar.text_input("Contact Email", value="wilnercharles3@gmail.com") 
daily_digest = st.sidebar.radio("Daily Digest Email", ["Yes, send me a daily summary", "No, I will check manually"])

# --- UI: MAIN PAGE ---
st.title("🤖 Steve's Personal Job Agent")
st.subheader("Phase 1: Executive Profile Verification")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
linkedin_url = st.text_input("LinkedIn Profile URL", value="https://www.linkedin.com/in/steve-etienne-92707420b/")

# --- UI: THE QUESTIONNAIRE ---
st.subheader("Phase 2: Target Preferences")
job_titles = st.text_input("Target Job Titles", value="Strategic Account Executive, Enterprise Sales Director, VP of Sales")
industry_keywords = st.text_input("Industry Keywords", value="B2B Sales, Hospitality Solutions, Multi-Location Partnerships")

st.markdown("#### 📊 Sales Structure & Metrics")
col1, col2 = st.columns(2)

with col1:
    role_type = st.radio("Career Track", [
        "Individual Contributor (Closing my own deals)", 
        "People Manager (Leading a sales team)",
        "Open to both"
    ], index=0)
    
    deal_size = st.selectbox("Target Deal Size / Complexity", [
        "Enterprise (Complex / 6-12 month cycles)", 
        "Mid-Market (Standard B2B)", 
        "SMB (High Volume / Fast cycles)"
    ], index=0)

with col2:
    travel_pct = st.slider("Maximum Travel % (Trade shows, client visits)", 
                           min_value=0, max_value=100, value=25, step=5)
    
    base_salary = st.number_input("Minimum Base Salary (Before Commission)", 
                                  min_value=50000, max_value=300000, value=120000, step=10000)

# --- UI: THE GUARDRAILS ---
st.subheader("Phase 3: Autonomy & Remote Guardrails")
st.info("💡 I've pre-programmed your core dealbreakers based on our last chat. The AI will read between the lines of job descriptions to filter out rigid corporate cultures.")

remote_policy = st.selectbox("Remote Policy Requirement", [
    "100% Remote (Work from Anywhere / Global)", 
    "100% Remote (Country-Specific / Geofenced)", 
    "Hybrid / Flexible"
], index=0)

dealbreakers = st.text_area("Non-Negotiables / Dealbreakers", 
    value="Strictly requires a high-trust, asynchronous environment. Must allow working abroad for extended periods (e.g., Kenya). Needs full autonomy over the complex sales pipeline—no micromanagement, invasive CRM tracking, or bait-and-switch return-to-office mandates. Evaluating based on full-cycle revenue growth and output, not daily screen time.",
    height=140)

# --- UI: THE DREAM SCENARIO ---
st.subheader("Phase 4: The Dream Scenario (Deal Sweeteners)")
st.info("🚀 Let's talk upside. If the AI finds a role that hits these metrics, it will flag it as a 'Top Tier Match'.")

col3, col4 = st.columns(2)

with col3:
    target_ote = st.number_input("Target OTE (Base + Commission)", 
                                  min_value=100000, max_value=500000, value=250000, step=25000)
    
    company_stage = st.selectbox("Ideal Company Stage", [
        "Open to Any",
        "Pre-IPO / High Equity Startup (High Risk/Reward)", 
        "Established Enterprise (Fortune 500 Stability)",
        "Mid-Market / High Growth"
    ])

with col4:
    dream_companies = st.text_area("🎯 'Sniper Mode' (Dream Companies)", 
                                   placeholder="e.g., Salesforce, Marriott Corporate, Toast... \n\nIf these companies post a role, the AI will alert you immediately.",
                                   height=110)

# --- ACTION: THE LIVE SCANNER ---
if st.button("Run Deep Scan & Save Preferences"):
    if uploaded_file is not None and job_titles:
        if supabase:
            try:
                with st.spinner("Injecting executive profile and strict guardrails into the AI Brain..."):
                    file_bytes = uploaded_file.getvalue()
                    supabase.storage.from_("resumes").upload(uploaded_file.name, file_bytes, {"upsert": "true"})
                
                st.success("✅ Executive profile saved.")
                st.divider()
                
                st.subheader("📡 Live Market Radar (Instant Results)")
                primary_title = job_titles.split(',')[0] if job_titles else 'Director'
                
                with st.spinner(f"Scraping global boards for {primary_title} roles and generating strict 5-star rubrics..."):
                    raw_jobs = get_live_jobs(primary_title)
                    valid_matches = []
                    email_html_matches = []
                    
                    if not raw_jobs:
                        job_matches_text = "No remote jobs found matching that title right now. We will check again tomorrow!"
                    else:
                        for job in raw_jobs:
                            # Send to Gemini
                            ai_summary = grade_job_with_ai(job, dealbreakers, target_ote, industry_keywords)
                            
                            if ai_summary:
                                title = job.get('title', 'Unknown Title')
                                company = job.get('company_name', 'Unknown Company')
                                location = job.get('location', 'Remote')
                                
                                apply_options = job.get('apply_options', [])
                                apply_link = apply_options[0].get('link') if apply_options else f"https://www.google.com/search?q={title.replace(' ', '+')}+{company.replace(' ', '+')}+job"
                                
                                # 1. Streamlit UI Format
                                match_info = f"### {title} @ {company}\n"
                                match_info += f"* **Location:** {location}\n"
                                match_info += f"{ai_summary}\n"
                                match_info += f"\n* **Apply Here:** [Click to Apply]({apply_link})\n"
                                match_info += "---\n"
                                valid_matches.append(match_info)
                                
                                # 2. Email HTML Format (Converting markdown to clean HTML)
                                html_info = f"<h3 style='color:#2C3E50;'>{title} @ {company}</h3>"
                                html_info += f"<p><b>Location:</b> {location}</p>"
                                
                                # Simple parser to make the AI Markdown look beautiful in email
                                for line in ai_summary.split('\n'):
                                    if line.startswith('**') and not line.startswith('** '):
                                        html_info += f"<h4 style='color:#34495E; margin-bottom: 2px;'>{line.replace('**', '')}</h4>"
                                    elif line.startswith('* '):
                                        clean_line = line[2:].replace('**', '<b>').replace('**', '</b>')
                                        html_info += f"<li style='margin-bottom: 5px;'>{clean_line}</li>"
                                    elif line.strip() != "":
                                        html_info += f"<p>{line}</p>"
                                        
                                html_info += f"<br><a href='{apply_link}' style='display:inline-block; padding:10px 15px; background-color:#28B463; color:white; text-decoration:none; border-radius:5px;'><b>Apply Here</b></a><br><br><hr>"
                                email_html_matches.append(html_info)
                        
                        if valid_matches:
                            job_matches_text = "\n".join(valid_matches)
                            email_jobs_text = "".join(email_html_matches)
                        else:
                            job_matches_text = "Scanned 5 recent remote jobs, but none passed your strict guardrails (all were 3 stars or below). Protecting your inbox from micromanagement!"
                            email_jobs_text = f"<p>{job_matches_text}</p>"
                
                st.markdown(job_matches_text)
                
                if valid_matches:
                    st.success("🎯 High-tier matches found! Dispatching detailed rubrics to your inbox...")
                else:
                    st.info("🛡️ Scan complete. No jobs passed the filter today.")

                send_confirmation_email(contact_email, job_titles, dealbreakers, email_jobs_text)
                    
            except Exception as e:
                st.error(f"Error during scan: {e}")
        else:
            st.error("🚨 Supabase Connection Failed: Your .env file is missing.")
    else:
        st.warning("⚠️ Please upload a resume and fill out at least your Target Job Titles.")