import os
import streamlit as st
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

print("📦 Starting Streamlit UI...")

st.title("🚀 Streamlit + Twilio is Running!")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

st.write("TWILIO_SID loaded:", TWILIO_SID is not None)

if TWILIO_SID and TWILIO_AUTH_TOKEN:
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        acc = client.api.accounts(TWILIO_SID).fetch()
        st.success(f"✅ Twilio connected! Account: {acc.friendly_name}")
    except TwilioRestException as e:
        st.error(f"❌ Twilio error: {e.msg}")
    except Exception as ex:
        st.error(f"❌ Unexpected error: {str(ex)}")
else:
    st.warning("⚠️ Twilio credentials not found in environment.")
