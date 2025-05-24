import os
import streamlit as st
import pandas as pd
from twilio.rest import Client

# --- Branding ---
st.set_page_config(page_title="🚀 Voice Campaign Center", page_icon="📞", layout="centered")
st.markdown("""
<style>
body {background-color: #f6f9fc;}
[data-testid="stSidebar"] > div:first-child {
    background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
[data-testid="stAppViewContainer"] {
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #333;
}
.block-container {
    padding: 2rem 2rem 2rem 2rem;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("📞 TruckTaxOnline.com - Campaign DashboardCampaign Dashboard")
st.caption("Powering automated voice outreach with Twilio + Streamlit")

# --- Upload section ---
st.subheader("📁 Upload Customer List")
uploaded_excel = st.file_uploader("Choose a CSV or Excel file with a 'Phone' column:", type=["csv", "xlsx"])

# --- Start button ---
deploy_btn = st.button("🚀 Launch Voice Campaign")

# --- Twilio credentials ---
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# --- Static hosted audio ---
audio_url = "https://raw.githubusercontent.com/sandhyasneha/streamlit-call-campaign/main/HumeAI_voice-preview_prefile.wav"

# --- Load numbers ---
@st.cache_data
def load_phone_numbers(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df['Phone'].dropna().astype(str).tolist()

# --- Main Logic ---
if deploy_btn:
    if not uploaded_excel:
        st.warning("Please upload your phone list first.")
    else:
        phone_numbers = load_phone_numbers(uploaded_excel)
        st.success(f"Preparing to call {len(phone_numbers)} customers...")

        for number in phone_numbers:
            try:
                call = client.calls.create(
                    to=number,
                    from_=TWILIO_PHONE_NUMBER,
                    twiml=f'<Response><Play>{audio_url}</Play></Response>'
                )
                st.info(f"📞 Calling {number}... Call SID: {call.sid}")
            except Exception as e:
                st.error(f"❌ Failed to call {number}: {e}")

        st.success("✅ Campaign launched successfully!")
