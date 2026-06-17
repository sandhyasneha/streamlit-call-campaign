import os
import time
from datetime import datetime
from urllib.parse import urlencode

import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
import pandas as pd
import plivo
import streamlit as st

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="TruckTaxOnline 2290 Call Campaign",
    page_icon="📞",
    layout="centered",
)

st.markdown("""
<style>
body {background-color: #f6f9fc;}
[data-testid="stSidebar"] > div:first-child {
    background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.block-container {
    padding: 2rem;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Helpers ----------------
def get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def normalize_phone(phone: str) -> str:
    phone = str(phone).strip()
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.endswith(".0"):
        phone = phone[:-2]
    if not phone.startswith("+"):
        phone = "+" + phone
    return phone


@st.cache_data
def load_phone_numbers(file):
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    if "Phone" not in df.columns:
        raise ValueError("CSV/Excel must contain a column named 'Phone'.")

    return [normalize_phone(x) for x in df["Phone"].dropna().tolist()]


def build_answer_url(base_url: str, audio_url: str) -> str:
    base_url = base_url.strip()
    if not base_url:
        raise ValueError("PLIVO_XML_URL is missing.")
    query = urlencode({"audio": audio_url})
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{query}"

# ---------------- Header ----------------
st.image("https://www.trucktaxonline.com/assets/logo.png", width=200)
st.title("📢 TruckTaxOnline — 2290 Call Campaign")
st.markdown("Reach truckers faster with automated voice calls for 2290 tax reminders.")

# ---------------- Credentials ----------------
PLIVO_AUTH_ID = get_env("PLIVO_AUTH_ID")
PLIVO_AUTH_TOKEN = get_env("PLIVO_AUTH_TOKEN")
PLIVO_FROM_NUMBER = normalize_phone(get_env("PLIVO_FROM_NUMBER", "+12544255576"))
PLIVO_XML_URL = get_env("PLIVO_XML_URL", "https://streamlit-call-campaign.onrender.com/plivo-answer")

cloudinary.config(
    cloud_name=get_env("CLOUDINARY_CLOUD_NAME"),
    api_key=get_env("CLOUDINARY_API_KEY"),
    api_secret=get_env("CLOUDINARY_API_SECRET"),
)

with st.expander("🔐 Environment Check"):
    st.write("PLIVO_AUTH_ID loaded:", bool(PLIVO_AUTH_ID))
    st.write("PLIVO_AUTH_TOKEN loaded:", bool(PLIVO_AUTH_TOKEN))
    st.write("PLIVO_FROM_NUMBER:", PLIVO_FROM_NUMBER)
    st.write("PLIVO_XML_URL:", PLIVO_XML_URL)
    st.write("CLOUDINARY_CLOUD_NAME loaded:", bool(get_env("CLOUDINARY_CLOUD_NAME")))
    st.write("CLOUDINARY_API_KEY loaded:", bool(get_env("CLOUDINARY_API_KEY")))
    st.write("CLOUDINARY_API_SECRET loaded:", bool(get_env("CLOUDINARY_API_SECRET")))

# ---------------- Upload section ----------------
st.subheader("📁 Upload Customer List")
uploaded_excel = st.file_uploader("Choose a CSV or Excel file with a 'Phone' column:", type=["csv", "xlsx"])

st.subheader("🔊 Upload Audio File")
uploaded_audio = st.file_uploader("Upload MP3 or WAV audio to play in calls:", type=["mp3", "wav"])

launch_btn = st.button("🚀 Launch Voice Campaign")

# ---------------- Main Logic ----------------
if launch_btn:
    call_logs = []

    if not PLIVO_AUTH_ID or not PLIVO_AUTH_TOKEN:
        st.error("❌ Plivo credentials missing. Add PLIVO_AUTH_ID and PLIVO_AUTH_TOKEN in Render Environment Variables, then redeploy.")
        st.stop()

    if not uploaded_excel or not uploaded_audio:
        st.warning("Please upload both phone list and audio file.")
        st.stop()

    try:
        phone_numbers = load_phone_numbers(uploaded_excel)
    except Exception as e:
        st.error(f"❌ Could not read phone list: {e}")
        st.stop()

    st.success(f"📞 Preparing to call {len(phone_numbers)} customers...")

    try:
        with st.spinner("Uploading audio to Cloudinary..."):
            result = cloudinary_upload(uploaded_audio, resource_type="video")
            audio_url = result["secure_url"]
    except Exception as e:
        st.error(f"❌ Audio upload failed: {e}")
        st.stop()

    try:
        answer_url = build_answer_url(PLIVO_XML_URL, audio_url)
        client = plivo.RestClient(auth_id=PLIVO_AUTH_ID, auth_token=PLIVO_AUTH_TOKEN)
    except Exception as e:
        st.error(f"❌ Plivo setup failed: {e}")
        st.stop()

    progress = st.progress(0)

    for index, number in enumerate(phone_numbers, start=1):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            response = client.calls.create(
                from_=PLIVO_FROM_NUMBER,
                to_=number,
                answer_url=answer_url,
                answer_method="GET",
            )
            request_uuid = getattr(response, "request_uuid", "-")
            call_logs.append({"Phone": number, "Status": "Success", "SID": request_uuid, "Time": timestamp})
            st.info(f"✅ Calling {number}... UUID: {request_uuid}")
        except Exception as e:
            call_logs.append({"Phone": number, "Status": f"Failed: {str(e)}", "SID": "-", "Time": timestamp})
            st.error(f"❌ Failed to call {number}: {e}")

        progress.progress(index / len(phone_numbers))
        time.sleep(1.1)  # Keeps calls near 1 CPS for Plivo.

    st.success("🎉 Campaign completed!")
    st.subheader("📊 Campaign Analytics")
    st.dataframe(pd.DataFrame(call_logs))

# ---------------- Footer ----------------
st.markdown("---")
st.markdown(
    "<center><small>Powered by <a href='https://www.trucktaxonline.com' target='_blank'>TruckTaxOnline.com</a></small></center>",
    unsafe_allow_html=True,
)
