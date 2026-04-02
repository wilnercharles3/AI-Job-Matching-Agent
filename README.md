## 🛠️ Troubleshooting & Installation Notes

### SDK Update Fix
If you encounter `ImportError: cannot import name 'genai' from 'google'`, it means the old Gemini SDK is interfering with the new one. 

**The Solution:**
1. Stop the Streamlit server (`Ctrl+C`).
2. Ensure your virtual environment is active: `source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows).
3. Run the following:
   ```bash
   pip uninstall google-generativeai
   pip install google-genai requests