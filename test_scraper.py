import os
import requests
from dotenv import load_dotenv

# Load your secret SerpApi Key
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

print("🚀 Pinging SerpApi for Remote Executive Jobs...")

# The exact question we are asking the Google Jobs API
url = f"https://serpapi.com/search.json?engine=google_jobs&q=Strategic+Account+Executive+Remote&hl=en&api_key={SERPAPI_KEY}"

# Send the request and get the data
response = requests.get(url)
data = response.json()

# Check if we successfully found jobs
if "jobs_results" in data:
    top_job = data["jobs_results"][0]
    print("\n✅ SUCCESS! Connection established.")
    print("🎯 Top Job Found:")
    print(f"Title: {top_job.get('title')}")
    print(f"Company: {top_job.get('company_name')}")
    print(f"Location: {top_job.get('location')}")
else:
    print("\n❌ FAILED. Something went wrong. Check your API key!")