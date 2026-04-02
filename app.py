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

# --- INITIALIZE SESSION STATE ---
if "job_results" not in st.session_state:
    st.session_state.job_results = []
if "graveyard" not in st.session_state:
    st.session_state.graveyard = []
if "scan_message" not in st.session_state:
    st.session_state.scan_message = ""

# --- API SETUP ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Clients
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# --- ENGINES ---
def get_live_jobs(query, limit=20):
    if not SERPAPI_KEY: return []
    safe_query = query.replace(" ", "+") + "+Remote"
    url = f"https://serpapi.com/search.json?engine=google_jobs&q={safe_query}&hl=en&api_key={SERPAPI_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("jobs_results", [])[:limit]
    except: return []

def grade_job_with_ai(job, dealbreakers, target_ote, industry_keywords):
    if not ai_client: return None
    title, company = job.get('title'), job.get('company_name')
    desc = job.get('description', '')
    
    # Intuitive OTE Logic
    ote_val = "Any / Not Filtered" if target_ote == 0 else f"${target_ote}+"
    ote_instruction = f"Target OTE: {ote_val}. Only fail if significantly lower than target." if target_ote > 0 else "OTE is set to 'Any'. Do not filter by pay."

    prompt = f"""
    Review as an executive headhunter:
    - Dealbreakers: {dealbreakers}
    - Keywords: {industry_keywords}
    - {ote_instruction}
    - Ratio Check: If Base Salary < 50% of OTE, fail as 'Commission Trap'.

    Job: {title} @ {company}
    Desc: {desc[:2000]}

    Fail format: "FAIL - [Reason]"
    Pass format: 
    * **Overall Rating:** [Stars]
    * **Company Intel:** [Summary]
    **📊 Rubric (1-5)**
    * 💰 **Pay:** [Score] - [Detail]
    * 🌍 **Remote:** [Score] - [Detail]
    * 🤝 **Support:** [Score] - [Detail]
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return response.text.strip()
    except: return None

def send_email(to, subject, body):
    if not EMAIL_SENDER: return False
    msg = MIMEText(f"<html><body>{body}</body></html>", 'html')
    msg['Subject'], msg['From'], msg['To'] = subject, EMAIL_SENDER, to
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to, msg.as_string())
        return True
    except: return False

# --- UI ---
st.title("🤖 Steve's Personal Job Agent")
st.subheader("Executive Profile & Guardrails")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_titles = st.text_input("Target Job Titles", "Strategic Account Executive, VP of Sales")
industry_keywords = st.text_input("Industry Keywords", "B2B Sales, SaaS")

c1, c2 = st.columns(2)
with c1:
    # Defaulting to 0 but displaying as "Any"
    min_base = st.number_input("Min Base Salary", value=0, step=10000, help="Leave at 0 for 'Any'")
    if min_base == 0: st.caption("Current: **Any**")
with c2:
    target_ote = st.number_input("Target OTE", value=0, step=10000, help="Leave at 0 for 'Any'")
    if target_ote == 0: st.caption("Current: **Any**")

dealbreakers = st.text_area("Dealbreakers", "100% Remote, Must allow work from Kenya, No micromanagement.")

# --- THE COMMAND CENTER (UX OPTIMIZED) ---
st.divider()
# Use a column layout to make Deep Scan the primary focus
col_main, col_side = st.columns([2, 1])

with col_main:
    # Primary Button (Highlighted)
    deep_scan = st.button("🚀 Run Deep Scan & Save Preferences", use_container_width=True, type="primary")

with col_side:
    # Secondary Button (Less prominent)
    quick_feed = st.button("⚡ Instant Jobs Now", use_container_width=True)

# --- LOGIC ---
if deep_scan or quick_feed:
    st.session_state.job_results, st.session_state.graveyard = [], []
    with st.spinner("Analyzing market..."):
        raw = get_live_jobs(job_titles.split(',')[0], limit=20)
        for j in raw:
            res = grade_job_with_ai(j, dealbreakers, target_ote, industry_keywords)
            if res and res.startswith("FAIL"):
                st.session_state.graveyard.append(f"❌ {j['title']}: {res[7:]}")
            elif res:
                link = j.get('apply_options', [{}])[0].get('link', '#')
                st.session_state.job_results.append({"ui": f"### {j['title']} @ {j['company_name']}\n{res}\n\n[Apply]({link})", "html": f"<h3>{j['title']}</h3>{res}<br><a href='{link}'>Apply</a><hr>"})
    
    st.session_state.scan_message = f"✅ Found {len(st.session_state.job_results)} matches."
    if deep_scan and st.session_state.job_results:
        send_email(contact_email, "🤖 Executive Match Report", "".join([j['html'] for j in st.session_state.job_results]))

# --- OUTPUT ---
if st.session_state.scan_message: st.info(st.session_state.scan_message)

if st.session_state.graveyard:
    if st.toggle("👁️ Show Graveyard (Filtered Out)"):
        for d in st.session_state.graveyard: st.error(d)

if st.session_state.job_results:
    st.divider()
    fwd_list = []
    for idx, j in enumerate(st.session_state.job_results):
        st.markdown(j["ui"])
        if st.checkbox("📥 Select to forward", value=True, key=f"f_{idx}"): fwd_list.append(j)
    
    st.subheader("📤 Forward Results")
    target = st.text_input("Forward to:", placeholder="email@example.com")
    if st.button("📨 Send Forward"):
        if send_email(target, "FWD: AI Job Matches", "".join([j['html'] for j in fwd_list])):
            st.success("Sent!")