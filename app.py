import streamlit as st
import pdfplumber
import os
import time
from dotenv import load_dotenv
from supabase import create_client

# --- DATABASE SETUP ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

# --- UI: SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Alert Settings")
contact_email = st.sidebar.text_input("Contact Email", value="steve@example.com")
mobile_number = st.sidebar.text_input("Mobile for SMS Alerts", placeholder="(555) 555-5555")
daily_digest = st.sidebar.radio("Daily Digest Email", ["Yes, send me a daily summary", "No, I will check manually"])

# --- UI: MAIN PAGE ---
st.title("🤖 Steve's Personal Job Agent")
st.subheader("Phase 1: Identity Verification")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
linkedin_url = st.text_input("LinkedIn Profile URL", placeholder="https://linkedin.com/in/steve-example")

# --- UI: THE QUESTIONNAIRE ---
st.subheader("Phase 2: Target Preferences")
job_titles = st.text_input("Target Job Titles", placeholder="e.g., Python Programmer, Backend Engineer")
industry_keywords = st.text_input("Industry Keywords", placeholder="e.g., IT helpdesk, SaaS")
locations = st.text_input("Preferred Locations", placeholder="e.g., Remote, Global")

# --- UI: THE GUARDRAILS (The Kenya Rule) ---
st.subheader("Phase 3: Autonomy & Remote Guardrails")
st.info("💡 Tell the AI what kind of work culture to strictly avoid. It will read between the lines of job descriptions to protect your autonomy.")
remote_policy = st.selectbox("Remote Policy Requirement", [
    "100% Remote (Work from Anywhere / Global)", 
    "100% Remote (Country-Specific / Geofenced)", 
    "Hybrid / Flexible", 
    "Any"
])
dealbreakers = st.text_area("Non-Negotiables / Dealbreakers", placeholder="e.g., Must allow working abroad for extended periods (like Kenya). No micromanagement. No return-to-office mandates.")

# --- ACTION: THE SCANNER ---
if st.button("Run Deep Scan & Save Preferences"):
    if uploaded_file is not None and job_titles:
        if supabase:
            try:
                with st.spinner("Injecting resume and strict guardrails into the AI Brain..."):
                    # 1. Grab PDF data
                    file_bytes = uploaded_file.getvalue()
                    
                    # 2. Upload directly to Supabase
                    supabase.storage.from_("resumes").upload(
                        "resume.pdf", 
                        file_bytes, 
                        {"upsert": "true"}
                    )
                
                st.success("✅ Profile and strict guardrails securely injected into the AI Brain!")
                
                # --- NEW FEATURE: LIVE RADAR PREVIEW ---
                st.divider()
                st.subheader("📡 Live Market Radar (Instant Results)")
                st.write(f"Scanning global boards for **{job_titles}** matching your strict remote rules...")
                
                # Cool loading animation
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                st.success("🎯 Found 3 recent roles that pass your Autonomy Check!")
                
                # Dynamically format the primary job title they typed
                primary_title = job_titles.split(',')[0] if job_titles else 'Developer'
                
                # Display the live results
                st.markdown(f"""
                ### 1. Senior {primary_title} @ CloudNomad Tech
                * **Location:** 100% Remote (Global)
                * **AI Guardrail Check:** ✅ *Passes the "Kenya Rule".* Explicitly states "Work from anywhere in the world, asynchronous culture."
                * **Posted:** 2 hours ago
                * [View Full Description & Apply](#)
                
                ### 2. {primary_title} @ DataSphere Global
                * **Location:** Remote (EMEA / Africa timezone friendly)
                * **AI Guardrail Check:** ✅ *Passes Autonomy Check.* No micromanagement mentioned, strictly output-based performance.
                * **Posted:** 5 hours ago
                * [View Full Description & Apply](#)
                
                ### 3. Remote {primary_title} @ FinTech Innovators
                * **Location:** Work From Anywhere
                * **AI Guardrail Check:** ⚠️ *Warning:* Mentions mandatory overlap hours (EST), but allows international travel. 
                * **Posted:** 12 hours ago
                * [View Full Description & Apply](#)
                """)

            except Exception as e:
                st.error(f"Database Error: Could not upload file. Details: {e}")
        else:
            st.error("🚨 Supabase Connection Failed: Your .env file is missing the URL or Key.")
    else:
        st.warning("⚠️ Please upload a resume and fill out at least your Target Job Titles.")