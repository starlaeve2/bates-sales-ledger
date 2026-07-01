import streamlit as st
import PIL.Image
import io
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions

# 1. Configuration
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

# Configure the client using Streamlit's secure secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- Helper Functions ---

# Image processing to stay under token limits
def process_image(uploaded_file):
    img = PIL.Image.open(uploaded_file)
    max_size = 1024
    if img.width > max_size:
        ratio = max_size / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_size, new_height), PIL.Image.Resampling.LANCZOS)
    return img

# Retry-enabled API call
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(exceptions.ResourceExhausted),
    reraise=True
)
def get_ai_response(prompt, image):
    return model.generate_content([prompt, image])

# --- Main App Logic ---
st.title("Bates Estates Ledger 📸")

# Use camera input instead of file uploader
img_file = st.camera_input("Take a photo of the item")

if img_file is not None:
    # Process the image
    processed_img = process_image(img_file)
    
    prompt = "List the main physical items in this image as a comma-separated list."
    
    try:
        with st.spinner("AI is itemizing..."):
            # Call the retry-enabled function
            response = get_ai_response(prompt, processed_img)
            st.session_state.temp_description = response.text.strip()
            st.write(st.session_state.temp_description)
    except exceptions.ResourceExhausted:
        st.error("Still hitting limits. Please wait a moment and try again.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.subheader("Edit & Submit")
# (Rest of your existing submit logic goes here)
