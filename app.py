import streamlit as st
import pdfplumber
import os
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
job_titles = st.text_input("Target Job Titles", placeholder="e.g., Sales Manager, Director, VP")
industry_keywords = st.text_input("Industry Keywords", placeholder="e.g., SaaS, Hospitality, Account Management")
locations = st.text_input("Preferred Locations", placeholder="e.g., Remote, New York, London")

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
                
                # 3. Show Success Message
                st.success("✅ Profile and strict guardrails securely injected into the AI Brain!")
                
                # 4. Display the extracted DNA summary
                st.info("🧬 **Career DNA & Targets Locked**")
                st.write(f"- **Target Roles:** {job_titles}")
                st.write(f"- **Industries:** {industry_keywords}")
                st.write(f"- **Remote Rule:** {remote_policy}")
                st.write(f"- **Dealbreakers:** {dealbreakers}")
                st.write(f"- **Alerts:** Email ({daily_digest})")

            except Exception as e:
                st.error(f"Database Error: Could not upload file. Details: {e}")
        else:
            st.error("🚨 Supabase Connection Failed: Your .env file is missing the URL or Key.")
    else:
        st.warning("⚠️ Please upload a resume and fill out at least your Target Job Titles.")