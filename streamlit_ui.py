import os
import streamlit as st
import pandas as pd
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from tempfile import NamedTemporaryFile

# Load Twilio credentials from environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

st.set_page_config(page_title="📞 Call Campaign Dashboard", layout="centered")
st.title("📞 AI Call Campaign Launcher")

st.markdown("Upload a phone list and an audio file to launch your Twilio call campaign.")

# Upload Excel file
uploaded_excel = st.file_uploader("Upload Customer List (Excel or CSV)", type=["csv", "xlsx"])

# Upload audio file
uploaded_audio = st.file_uploader("Upload Audio File (MP3 or WAV)", type=["mp3", "wav"])

# Campaign trigger button
deploy_btn = st.button("🚀 Launch Call Campaign")

# Helper to parse uploaded numbers
@st.cache_data
def load_phone_numbers(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df['Phone'].dropna().astype(str).tolist()

# Main action
if deploy_btn:
    if not uploaded_excel or not uploaded_audio:
        st.warning("Please upload both phone list and audio file.")
    else:
        phone_numbers = load_phone_numbers(uploaded_excel)

        # Temporarily save audio file
        with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_audio.name)[-1]) as temp_audio:
            temp_audio.write(uploaded_audio.read())
            audio_path = temp_audio.name

        st.success(f"Preparing to call {len(phone_numbers)} numbers...")

        for number in phone_numbers:
            try:
                call = client.calls.create(
                    to=number,
                    from_=TWILIO_PHONE_NUMBER,
                    twiml=f'<Response><Play>{audio_path}</Play></Response>'
                )
                st.info(f"📞 Calling {number}... SID: {call.sid}")
            except Exception as e:
                st.error(f"❌ Failed to call {number}: {e}")

        st.success("✅ Campaign launched!")
