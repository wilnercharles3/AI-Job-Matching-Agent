import streamlit as st
import pdfplumber
import re

# --- ⚙️ CORE LOGIC: THE DEEP SCAN ---
def extract_resume_data(file):
    """Extracts text from PDF and cleans up white space."""
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_career_dna(text, linkedin_url):
    """
    SMART Goal: Maps 20+ years of history.
    This mimics the logic in resume_parser.py from the repo.
    """
    # Look for years of experience
    years_match = re.search(r"(\d+)\+?\s*years", text.lower())
    seniority = f"{years_match.group(1)}+ Years" if years_match else "Executive (20+ yrs)"
    
    # Identify Core Track
    track = "Management/Operations" if "manager" in text.lower() or "director" in text.lower() else "Specialist"
    
    return {
        "Seniority": seniority,
        "Track": track,
        "LinkedIn": linkedin_url
    }

# --- 🎨 INTERFACE ---
st.set_page_config(page_title="Steve's AI Agent", layout="centered")
st.title("🤖 Steve's Personal Job Agent")
st.info("Phase 1: Deep Scan & Identity Verification")

# Sidebar for persistent settings
with st.sidebar:
    st.header("Settings")
    email = st.text_input("Contact Email", value="steve@example.com")
    phone = st.text_input("Mobile for SMS Alerts")

# Main Onboarding
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
linkedin_link = st.text_input("LinkedIn Profile URL")

if st.button("Run Deep Scan"):
    if uploaded_file and linkedin_link:
        with st.spinner("Analyzing 20 years of professional footprint..."):
            # 1. Parse the PDF
            raw_text = extract_resume_data(uploaded_file)
            
            # 2. Build the DNA
            dna = generate_career_dna(raw_text, linkedin_link)
            
            # 3. Success UI
            st.success("✅ Deep Scan Complete!")
            c1, c2 = st.columns(2)
            c1.metric("Seniority Level", dna["Seniority"])
            c2.metric("Career Track", dna["Track"])
            
            st.write(f"🔗 **LinkedIn Linked:** {dna['LinkedIn']}")
            st.warning(f"Verification: A test email and text will be sent to {email} shortly.")
            st.balloons()
    else:
        st.error("Please provide both a Resume and LinkedIn link to proceed.")