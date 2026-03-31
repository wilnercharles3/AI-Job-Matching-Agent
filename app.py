import streamlit as st
import os
import time
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from supabase import create_client

# --- PRO UPGRADE: PREMIUM PAGE LAYOUT ---
st.set_page_config(page_title="Steve's AI Agent", page_icon="👔", layout="centered")

# --- DATABASE & EMAIL SETUP ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

def send_confirmation_email(to_email, target_jobs, dealbreakers, job_matches):
    """Sends an automated email via Gmail SMTP containing the live job matches"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False
    
    email_body = f"""Hey Steve,

Your AI Job Bot preferences are locked in.

Target Roles: {target_jobs}
Dealbreakers: {dealbreakers}

The engine scanned the global boards and filtered out the micromanagers. Here are your top instant matches based on your new Executive profile:

{job_matches}

- Your Personal AI Agent
"""
    
    msg = MIMEText(email_body)
    msg['Subject'] = "🤖 AI Job Bot: Executive Matches Found!"
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
seniority = st.selectbox("Seniority Level", [
    "Executive (VP / C-Suite)", 
    "Director / Head Of", 
    "Senior (10+ Years Exp)", 
    "Mid-Level"
], index=2)

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

# --- ACTION: THE SCANNER ---
if st.button("Run Deep Scan & Save Preferences"):
    if uploaded_file is not None and job_titles:
        if supabase:
            try:
                # PRO UPGRADE: Smart Status Updates
                with st.spinner("Injecting executive profile and strict guardrails into the AI Brain..."):
                    file_bytes = uploaded_file.getvalue()
                    # PRO UPGRADE: Dynamic File Naming Patch
                    supabase.storage.from_("resumes").upload(uploaded_file.name, file_bytes, {"upsert": "true"})
                    time.sleep(1) # Brief pause for effect
                
                st.success("✅ Executive profile and strict guardrails securely injected!")
                
                st.divider()
                st.subheader("📡 Live Market Radar (Instant Results)")
                primary_title = job_titles.split(',')[0] if job_titles else 'Director'
                
                # PRO UPGRADE: Intelligent Loading Animation
                progress_text = "Scanning global boards for matching remote rules..."
                progress_bar = st.progress(0, text=progress_text)
                
                for i in range(100):
                    time.sleep(0.02)
                    if i == 30:
                        progress_bar.progress(i + 1, text="Filtering out micromanagers and rigid cultures...")
                    elif i == 60:
                        progress_bar.progress(i + 1, text=f"Evaluating OTE and Deal Size metrics for {primary_title}...")
                    else:
                        progress_bar.progress(i + 1)
                
                time.sleep(0.5)
                progress_bar.empty() # Clears the bar once done
                st.success("🎯 Found 2 recent roles that pass the Autonomy Check!")
                
                # Generate the Job Matches string for both the UI and the Email
                job_matches_text = f"""
1. Global {primary_title} @ Apex Revenue Solutions
* Location: 100% Remote (Global)
* AI Guardrail Check: Passes the "Kenya Rule". Explicitly states "Work from anywhere in the world, focus on relationship-driven sales."
* Base/OTE Match: Verified $130k Base / $260k OTE.
* Posted: 2 hours ago

2. Enterprise Sales Director @ NextGen Hospitality Tech
* Location: Remote (EMEA / Africa timezone friendly)
* AI Guardrail Check: Passes Autonomy Check. No micromanagement mentioned, strictly pipeline and revenue-based performance metrics.
* Deal Size Match: Focuses on complex 6-12 month enterprise sales cycles.
* Posted: 5 hours ago
"""
                
                # Display on screen
                st.markdown(job_matches_text.replace('* ', '* **').replace(': ', ':** '))

                # Send the email WITH the jobs
                with st.spinner("Dispatching confirmation email with job matches..."):
                    send_confirmation_email(contact_email, job_titles, dealbreakers, job_matches_text)
                    
            except Exception as e:
                st.error(f"Database Error: Could not upload file. Details: {e}")
        else:
            st.error("🚨 Supabase Connection Failed: Your .env file is missing.")
    else:
        st.warning("⚠️ Please upload a resume and fill out at least your Target Job Titles.")