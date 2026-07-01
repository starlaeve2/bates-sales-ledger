import streamlit as st
import PIL.Image
from google.generativeai import GenerativeModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions
# 1. Configuration
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

# Configure the client using Streamlit's secure secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')
# --- Helper Functions ---

# 1. Image processing to stay under token limits
def process_image(uploaded_file):
    img = PIL.Image.open(uploaded_file)
    max_size = 1024
    if img.width > max_size:
        ratio = max_size / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_size, new_height), PIL.Image.Resampling.LANCZOS)
    return img

# 2. Retry-enabled API call
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(exceptions.ResourceExhausted),
    reraise=True
)
def get_ai_response(prompt, image):
    return model.generate_content([prompt, image])
