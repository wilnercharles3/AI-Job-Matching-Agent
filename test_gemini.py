import os
from google import genai
from dotenv import load_dotenv

# Load your secret Gemini API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("🧠 Waking up the New Gemini AI Brain...")

# Configure the new AI client
client = genai.Client(api_key=GEMINI_API_KEY)

# The Prompt (The Guardrails)
prompt = """
You are an executive sales headhunter protecting your client's time. 
Rate this job description from 1 to 5 Stars based on these dealbreakers:
- Must allow full autonomy (work from anywhere, e.g., Kenya).
- NO micromanagement or strict daily CRM activity tracking.
- High OTE potential ($200k+).

Job Title: Strategic Account Executive
Company: TestCorp
Description: We need a senior closer for complex enterprise deals. You manage your own pipeline and schedule—we care about closed revenue, not what time you log in. 100% remote work from anywhere in the world. OTE is $260k uncapped.

Return ONLY the star rating (e.g., ⭐⭐⭐⭐⭐) and a 1-sentence explanation.
"""

# Ask the AI to grade the job
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    print("\n✅ SUCCESS! The AI has spoken:")
    print(f"\n{response.text}")
except Exception as e:
    print(f"\n❌ FAILED. Error: {e}")