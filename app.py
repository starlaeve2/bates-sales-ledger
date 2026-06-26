import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuration
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

api_key = "AQ.Ab8RN6I25LS1VwayxsGJKf_lGU4DAZ7pCSP1417jdWC4S5AEqg"
genai.configure(api_key=api_key)
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
            # Strict prompt for comma-separated list
            prompt = "List the main physical items in this image as a comma-separated list. Do not include descriptions of people, hands, or actions. Just the items."
            response = model.generate_content([prompt, image])
            st.session_state.temp_description = response.text.strip()

    st.subheader("Confirm & Submit")
    st.info("Copy the list below, paste it into the form, fill in the price, and hit Submit.")
    st.code(st.session_state.temp_description)
    
    # Your Google Form integration
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe6ZMMMHJMaFB_R0Sjk13umUqjC50Bvq2eVSGMv9BO-_N8_fw/viewform?embedded=true"
    st.components.v1.iframe(form_url, height=600, scrolling=True)

    if st.button("Reset for New Item"):
        st.session_state.temp_description = ""
        st.rerun()
