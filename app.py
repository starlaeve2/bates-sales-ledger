import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import urllib.parse

# 1. Configuration
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

# Configure the client using Streamlit's secure secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

if "temp_description" not in st.session_state:
    st.session_state.temp_description = ""

st.title("📸 Quick Sale Ledger")

# 2. Camera Input
img_file = st.camera_input("Take a photo of the item")

if img_file is not None:
    if st.session_state.temp_description == "":
        with st.spinner("AI is itemizing..."):
            image = Image.open(io.BytesIO(img_file.getvalue()))
            prompt = "List the main physical items in this image as a comma-separated list."
            response = model.generate_content([prompt, image])
            st.session_state.temp_description = response.text.strip()

    st.subheader("Edit & Submit")
    
    # URL-encode the description for the form
    encoded_desc = urllib.parse.quote(st.session_state.temp_description)
    
    # Pre-filled link with only the Description field
    prefilled_url = (
        f"https://docs.google.com/forms/d/e/1FAIpQLSe6ZMMMHJMaFB_R0Sjk13umUqjC50Bvq2eVSGMv9BO-_N8_fw/viewform?embedded=true"
        f"&entry.1364187317={encoded_desc}"
    )
    
    st.components.v1.iframe(prefilled_url, height=600, scrolling=True)

    if st.button("Reset for New Item"):
        st.session_state.temp_description = ""
        st.rerun()
