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
st.sidebar.header("⚙️ Settings")
contact_email = st.sidebar.text_input("Contact Email", value="steve@example.com")
mobile_number = st.sidebar.text_input("Mobile for SMS Alerts", placeholder="(555) 555-5555")

# --- UI: MAIN PAGE ---
st.title("🤖 Steve's Personal Job Agent")
st.subheader("Phase 1: Identity Verification")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
linkedin_url = st.text_input("LinkedIn Profile URL", placeholder="https://linkedin.com/in/steve-example")

st.subheader("Phase 2: Target Preferences")
job_titles = st.text_input("Target Job Titles", placeholder="e.g., Sales Manager, Director, VP")
locations = st.text_input("Preferred Locations", placeholder="e.g., Remote, New York, London")

# --- ACTION: THE SCANNER ---
if st.button("Run Deep Scan & Save Preferences"):
    if uploaded_file is not None and job_titles and locations:
        if supabase:
            try:
                with st.spinner("Injecting resume and preferences into the AI Brain..."):
                    # 1. Grab PDF data
                    file_bytes = uploaded_file.getvalue()
                    
                    # 2. Upload directly to Supabase
                    supabase.storage.from_("resumes").upload(
                        "resume.pdf", 
                        file_bytes, 
                        {"upsert": "true"}
                    )
                
                # 3. Show Success Message
                st.success("✅ Profile securely injected into the AI Brain!")
                
                # 4. Display the extracted DNA summary
                st.info("🧬 **Career DNA & Targets Locked**")
                st.write(f"- **Target Roles:** {job_titles}")
                st.write(f"- **Locations:** {locations}")
                st.write(f"- **Contact Target:** {contact_email}")

            except Exception as e:
                st.error(f"Database Error: Could not upload file. Details: {e}")
        else:
            st.error("🚨 Supabase Connection Failed: Your .env file is missing the URL or Key.")
    else:
        st.warning("⚠️ Please upload a resume and fill out your job/location targets.")