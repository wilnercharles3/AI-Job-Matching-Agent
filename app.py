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

# --- INITIALIZE SESSION STATE (THE APP'S MEMORY) ---
if "job_results" not in st.session_state:
    st.session_state.job_results = []
if "scan_message" not in st.session_state:
    st.session_state.scan_message = ""

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
def get_live_jobs(query, limit=5):
    """Scrapes live remote jobs using SerpApi"""
    if not SERPAPI_KEY: return []
    safe_query = query.replace(" ", "+") + "+Remote"
    url = f"https://serpapi.com/search.json?engine=google_jobs&q={safe_query}&hl=en&api_key={SERPAPI_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("jobs_results", [])[:limit] 
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

    First, decide if this job is a 4 or 5-star overall match. If it is 1, 2, or 3 stars, strictly return ONLY the word "FAIL".
    
    If it passes, return an Executive Scorecard EXACTLY in this format using a strict 1 to 5 scale:
    
    * **Overall AI Rating:** [Insert 4 or 5 Stars]
    * **Company Intel:** [1 brief sentence summarizing what the company actually does/sells]
    
    **📊 Executive Rubric**
    * 💰 **Compensation ([Score]/5):** [1 sentence explaining base/OTE visibility]
    * 🌍 **Autonomy & Timezone ([Score]/5):** [1 sentence explaining if it's true remote/async or has limits]
    * 🤝 **Sales Support & Role ([Score]/5):** [1 sentence on if they have BDR support or if it's full-cycle]
    
    **🎯 Keyword Matches**
    * [Identify which of the specific Target Industry Keywords were found in the text. If none, say "No specific target keywords explicitly mentioned."]
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

def send_confirmation_email(to_email, target_jobs, job_matches, custom_subject="🤖 AI Job Bot: Live Executive Rubrics Found!"):
    """Sends an automated HTML email via Gmail SMTP"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    
    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2E86C1;">🤖 AI Job Bot: Executive Scan Complete</h2>
    <p>Hey there,</p>
    <p>Here are the latest AI-vetted job matches based on the Executive target profile.</p>
    <p><b>Target Roles:</b> {target_jobs}</p>
    <hr>
    <p>The engine scanned the global boards, filtered out the micromanagers, and generated custom rubrics:</p>
    <br>
    {job_matches}
    <br>
    <hr>
    <p><i>- Powered by Steve's AI Agent</i></p>
    </body>
    </html>
    """
    
    msg = MIMEText(email_body, 'html')
    msg['Subject'] = custom_subject
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

# --- ACTION: DUAL BUTTON SETUP ---
st.divider()
st.subheader("🚀 Command Center")

btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    instant_feed_clicked = st.button("⚡ Instant Jobs Now (Quick Feed)", use_container_width=True)

with btn_col2:
    deep_scan_clicked = st.button("Run Deep Scan & Save Preferences", use_container_width=True)


# --- LOGIC: FETCHING JOBS (TRIGGERS ON EITHER BUTTON) ---
if instant_feed_clicked or deep_scan_clicked:
    if job_titles:
        # 1. Clear memory for the new scan
        st.session_state.job_results = []
        st.session_state.scan_message = ""
        
        primary_title = job_titles.split(',')[0] if job_titles else 'Director'
        limit = 3 if instant_feed_clicked else 5
        
        with st.spinner(f"Scraping the global market for {primary_title} roles..."):
            raw_jobs = get_live_jobs(primary_title, limit=limit)
            
            if not raw_jobs:
                st.session_state.scan_message = "No remote jobs found matching that title right now."
            else:
                for job in raw_jobs:
                    ai_summary = grade_job_with_ai(job, dealbreakers, target_ote, industry_keywords)
                    if ai_summary:
                        title = job.get('title', 'Unknown Title')
                        company = job.get('company_name', 'Unknown Company')
                        location = job.get('location', 'Remote')
                        apply_options = job.get('apply_options', [])
                        apply_link = apply_options[0].get('link') if apply_options else f"https://www.google.com/search?q={title.replace(' ', '+')}+{company.replace(' ', '+')}+job"
                        
                        # Markdown Format (for the screen)
                        match_info = f"### {title} @ {company}\n"
                        match_info += f"* **Location:** {location}\n"
                        match_info += f"{ai_summary}\n"
                        match_info += f"\n* **Apply Here:** [Click to Apply]({apply_link})\n"
                        
                        # HTML Format (for the email)
                        html_info = f"<h3 style='color:#2C3E50;'>{title} @ {company}</h3>"
                        html_info += f"<p><b>Location:</b> {location}</p>"
                        for line in ai_summary.split('\n'):
                            if line.startswith('**') and not line.startswith('** '):
                                html_info += f"<h4 style='color:#34495E; margin-bottom: 2px;'>{line.replace('**', '')}</h4>"
                            elif line.startswith('* '):
                                clean_line = line[2:].replace('**', '<b>').replace('**', '</b>')
                                html_info += f"<li style='margin-bottom: 5px;'>{clean_line}</li>"
                            elif line.strip() != "":
                                html_info += f"<p>{line}</p>"
                        html_info += f"<br><a href='{apply_link}' style='display:inline-block; padding:10px 15px; background-color:#28B463; color:white; text-decoration:none; border-radius:5px;'><b>Apply Here</b></a><br><br><hr>"
                        
                        # Save to memory!
                        st.session_state.job_results.append({
                            "title": title,
                            "company": company,
                            "ui_text": match_info,
                            "html_text": html_info
                        })
                
                if st.session_state.job_results:
                    st.session_state.scan_message = "✅ Scan complete! Curated jobs loaded below."
                else:
                    st.session_state.scan_message = "🛡️ Scanned recent jobs, but none passed your strict AI guardrails. No junk allowed on your feed."

        # If it was a Deep Scan, we still run the database upload and auto-email
        if deep_scan_clicked:
            if supabase and uploaded_file is not None:
                file_bytes = uploaded_file.getvalue()
                supabase.storage.from_("resumes").upload(uploaded_file.name, file_bytes, {"upsert": "true"})
            
            if st.session_state.job_results:
                all_html = "".join([j["html_text"] for j in st.session_state.job_results])
                send_confirmation_email(contact_email, job_titles, all_html)
                st.session_state.scan_message += " (Sent full backup to your inbox!)"
    else:
        st.warning("⚠️ Please fill out your Target Job Titles first.")


# --- UI: DISPLAY RESULTS & FORWARDING CAPABILITY ---
if st.session_state.scan_message:
    st.info(st.session_state.scan_message)

# Only show this section if we have jobs in memory
if st.session_state.job_results:
    st.divider()
    st.subheader("📋 Your Curated Job Feed")
    
    selected_for_forwarding = []
    
    # Render jobs and their checkboxes
    for idx, job_data in enumerate(st.session_state.job_results):
        st.markdown(job_data["ui_text"])
        
        # Checkbox logic
        is_selected = st.checkbox(f"📥 Select {job_data['title']} to forward", value=True, key=f"chk_{idx}")
        if is_selected:
            selected_for_forwarding.append(job_data)
            
        st.markdown("---")
        
    # --- UI: THE FORWARDING ENGINE ---
    st.subheader("📤 Share / Forward Selected Jobs")
    st.markdown("Want to send specific jobs to a colleague or alternate email? Uncheck any jobs you don't want to send above, enter an email below, and hit forward.")
    
    fwd_col1, fwd_col2 = st.columns([2, 1])
    with fwd_col1:
        forward_email = st.text_input("Recipient Email:", placeholder="colleague@example.com")
    with fwd_col2:
        st.markdown("<br>", unsafe_allow_html=True) # visual alignment hack
        forward_button = st.button("📨 Forward Selected Jobs", use_container_width=True)
        
    if forward_button:
        if not selected_for_forwarding:
            st.warning("⚠️ Please select at least one job above to forward.")
        elif not forward_email:
            st.warning("⚠️ Please enter a recipient email.")
        else:
            with st.spinner(f"Forwarding {len(selected_for_forwarding)} jobs to {forward_email}..."):
                fwd_html = "".join([j["html_text"] for j in selected_for_forwarding])
                success = send_confirmation_email(
                    to_email=forward_email, 
                    target_jobs=job_titles, 
                    job_matches=fwd_html, 
                    custom_subject="FWD: 🤖 AI Job Bot Matches"
                )
                if success:
                    st.success(f"✅ Successfully forwarded {len(selected_for_forwarding)} jobs to {forward_email}!")
                else:
                    st.error("❌ Failed to forward email. Check your SMTP settings.")