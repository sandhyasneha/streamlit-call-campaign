import plivo
import time
PLIVO_AUTH_ID = os.getenv("PLIVO_AUTH_ID")
PLIVO_AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN")
PLIVO_FROM_NUMBER = os.getenv("PLIVO_FROM_NUMBER")
PLIVO_XML_URL = os.getenv("PLIVO_XML_URL")

client = plivo.RestClient(
    auth_id=PLIVO_AUTH_ID,
    auth_token=PLIVO_AUTH_TOKEN
)


from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.utils import cloudinary_url
import cloudinary


# --- Page Config ---
st.set_page_config(
    page_title="TruckTaxOnline 2290 Call Campaign",
    page_icon="📞",
    layout="centered"
)

# --- Custom Styling ---
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
    padding: 2rem;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.image("https://www.trucktaxonline.com/assets/logo.png", width=200)
st.title("📢 TruckTaxOnline — 2290 Call Campaign")
st.markdown("Reach truckers faster with automated voice calls for 2290 tax reminders.")

# --- Upload section ---
st.subheader("📁 Upload Customer List")
uploaded_excel = st.file_uploader("Choose a CSV or Excel file with a 'Phone' column:", type=["csv", "xlsx"])

st.subheader("🔊 Upload Audio File")
uploaded_audio = st.file_uploader("Upload MP3 or WAV audio to play in calls:", type=["mp3", "wav"])

# --- Launch Campaign Button ---
deploy_btn = st.button("🚀 Launch Voice Campaign")

# --- PLIVO Credentials ---
PLIVO_AUTH_ID = os.getenv("PLIVO_AUTH_ID")
PLIVO_AUTH_TOKEN = os.getenv("PLIVO_AUTH_TOKEN")
PLIVO_PHONE_NUMBER = os.getenv("PLIVO_PHONE_NUMBER")

# --- Cloudinary Config ---
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# --- Load phone numbers ---
@st.cache_data
def load_phone_numbers(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df['Phone'].dropna().astype(str).tolist()

# --- Analytics DataFrame ---
call_logs = []

# --- Main Logic ---
if deploy_btn:
    if not uploaded_excel or not uploaded_audio:
        st.warning("Please upload both phone list and audio file.")
    else:
        phone_numbers = load_phone_numbers(uploaded_excel)
        st.success(f"📞 Preparing to call {len(phone_numbers)} customers...")

        # Upload audio to Cloudinary
        with st.spinner("Uploading audio to cloud..."):
            res = cloudinary_upload(uploaded_audio, resource_type="video")
            audio_url = res['secure_url']

        for number in phone_numbers:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                
response = client.calls.create(
    from_=PLIVO_FROM_NUMBER,
    to_=number,
    answer_url=f"{PLIVO_XML_URL}?audio={audio_url}",
    answer_method="GET"
)

time.sleep(1.1)


                call_logs.append({"Phone": number, "Status": "Success", "SID": call.sid, "Time": timestamp})
                st.info(f"✅ Calling {number}... SID: {call.sid}")
            except Exception as e:
                call_logs.append({"Phone": number, "Status": f"Failed: {str(e)}", "SID": "-", "Time": timestamp})
                st.error(f"❌ Failed to call {number}: {e}")

        st.success("🎉 Campaign launched successfully!")

        # --- Display Analytics ---
        st.subheader("📊 Campaign Analytics")
        st.dataframe(pd.DataFrame(call_logs))

# --- Footer ---
st.markdown("---")
st.markdown(
    "<center><small>Powered by <a href='https://www.trucktaxonline.com' target='_blank'>TruckTaxOnline.com</a></small></center>",
    unsafe_allow_html=True
)
