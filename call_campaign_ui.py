import os
import time
from datetime import datetime
from urllib.parse import urlencode

import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
import pandas as pd
import plivo
import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="TruckTaxOnline 2290 Call Campaign",
    page_icon="📞",
    layout="centered",
)

# --- Custom Styling ---
st.markdown(
    """
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
    padding: 2rem;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Header ---
st.image("https://www.trucktaxonline.com/assets/logo.png", width=200)
st.title("📢 TruckTaxOnline — 2290 Call Campaign")
st.markdown("Reach truckers faster with automated voice calls for 2290 tax reminders.")

# --- Environment Variables ---
PLIVO_AUTH_ID = os.getenv("PLIVO_AUTH_ID", "").strip()
PLIVO_AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN", "").strip()
PLIVO_FROM_NUMBER = os.getenv("PLIVO_FROM_NUMBER", os.getenv("PLIVO_PHONE_NUMBER", "")).strip()
PLIVO_XML_URL = os.getenv("PLIVO_XML_URL", "").strip()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "").strip()
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "").strip()

# --- Cloudinary Config ---
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

# --- Upload section ---
st.subheader("📁 Upload Customer List")
uploaded_excel = st.file_uploader(
    "Choose a CSV or Excel file with a 'Phone' column:",
    type=["csv", "xlsx"],
)

st.subheader("🔊 Upload Audio File")
uploaded_audio = st.file_uploader(
    "Upload MP3 or WAV audio to play in calls:",
    type=["mp3", "wav"],
)

# --- Load phone numbers ---
@st.cache_data
def load_phone_numbers(file):
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    if "Phone" not in df.columns:
        raise ValueError("The uploaded file must contain a column named 'Phone'.")

    numbers = []
    for value in df["Phone"].dropna().astype(str).tolist():
        cleaned = value.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if cleaned.endswith(".0"):
            cleaned = cleaned[:-2]
        if cleaned:
            numbers.append(cleaned)
    return numbers


def validate_settings():
    missing = []
    if not PLIVO_AUTH_ID:
        missing.append("PLIVO_AUTH_ID")
    if not PLIVO_AUTH_TOKEN:
        missing.append("PLIVO_AUTH_TOKEN")
    if not PLIVO_FROM_NUMBER:
        missing.append("PLIVO_FROM_NUMBER")
    if not PLIVO_XML_URL:
        missing.append("PLIVO_XML_URL")
    if not CLOUDINARY_CLOUD_NAME:
        missing.append("CLOUDINARY_CLOUD_NAME")
    if not CLOUDINARY_API_KEY:
        missing.append("CLOUDINARY_API_KEY")
    if not CLOUDINARY_API_SECRET:
        missing.append("CLOUDINARY_API_SECRET")
    return missing


# --- Launch Campaign Button ---
deploy_btn = st.button("🚀 Launch Voice Campaign")

# --- Main Logic ---
if deploy_btn:
    missing_settings = validate_settings()

    if missing_settings:
        st.error("Missing Render environment variables: " + ", ".join(missing_settings))
    elif not uploaded_excel or not uploaded_audio:
        st.warning("Please upload both phone list and audio file.")
    else:
        try:
            phone_numbers = load_phone_numbers(uploaded_excel)
        except Exception as e:
            st.error(f"Could not read phone list: {e}")
            st.stop()

        if not phone_numbers:
            st.warning("No phone numbers found in the Phone column.")
            st.stop()

        st.success(f"📞 Preparing to call {len(phone_numbers)} customers...")

        # Upload audio to Cloudinary
        with st.spinner("Uploading audio to cloud..."):
            try:
                res = cloudinary_upload(uploaded_audio, resource_type="video")
                audio_url = res["secure_url"]
                st.success("Audio uploaded successfully.")
            except Exception as e:
                st.error(f"Audio upload failed: {e}")
                st.stop()

        client = plivo.RestClient(auth_id=PLIVO_AUTH_ID, auth_token=PLIVO_AUTH_TOKEN)
        call_logs = []
        progress = st.progress(0)

        for index, number in enumerate(phone_numbers, start=1):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                query_string = urlencode({"audio": audio_url})
                answer_url = f"{PLIVO_XML_URL}?{query_string}"

                response = client.calls.create(
                    from_=PLIVO_FROM_NUMBER,
                    to_=number,
                    answer_url=answer_url,
                    answer_method="GET",
                )

                call_id = getattr(response, "request_uuid", None) or getattr(response, "message_uuid", None) or str(response)

                call_logs.append({
                    "Phone": number,
                    "Status": "Success",
                    "Call ID": call_id,
                    "Time": timestamp,
                })
                st.info(f"✅ Calling {number}... Call ID: {call_id}")

                # Keep around 1 call per second for Plivo CPS limit
                time.sleep(1.1)

            except Exception as e:
                call_logs.append({
                    "Phone": number,
                    "Status": f"Failed: {str(e)}",
                    "Call ID": "-",
                    "Time": timestamp,
                })
                st.error(f"❌ Failed to call {number}: {e}")

            progress.progress(index / len(phone_numbers))

        st.success("🎉 Campaign process completed.")

        # --- Display Analytics ---
        st.subheader("📊 Campaign Analytics")
        st.dataframe(pd.DataFrame(call_logs), use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    "<center><small>Powered by <a href='https://www.trucktaxonline.com' target='_blank'>TruckTaxOnline.com</a></small></center>",
    unsafe_allow_html=True,
)
