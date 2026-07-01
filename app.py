import streamlit as st
import PIL.Image
import io
import gspread
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions
from oauth2client.service_account import ServiceAccountCredentials

# 1. Configuration
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

# Configure the client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-3.5-flash')

# --- Google Sheets Setup ---
def get_sheet_client():
    # Uses Streamlit secrets for credentials
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Bates Estates Ledger").sheet1 # Change "Bates Estates Ledger" to your sheet name

# --- Helper Functions ---
def process_image(uploaded_file):
    img = PIL.Image.open(uploaded_file)
    max_size = 1024
    if img.width > max_size:
        ratio = max_size / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_size, new_height), PIL.Image.Resampling.LANCZOS)
    return img

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

if 'temp_description' not in st.session_state:
    st.session_state.temp_description = ""

img_file = st.camera_input("Take a photo of the item")

if img_file is not None:
    processed_img = process_image(img_file)
    prompt = "List the main physical items in this image as a comma-separated list."
    
    try:
        with st.spinner("AI is itemizing..."):
            response = get_ai_response(prompt, processed_img)
            st.session_state.temp_description = response.text.strip()
    except Exception as e:
        st.error(f"Error: {e}")

# --- Edit & Submit Form ---
st.subheader("Edit & Submit")
with st.form("item_form"):
    edited_description = st.text_area("Item Description", value=st.session_state.temp_description)
    submit_button = st.form_submit_button("Submit to Ledger")

if submit_button:
    try:
        sheet = get_sheet_client()
        sheet.append_row([edited_description])
        st.success("Successfully added to the ledger!")
        st.session_state.temp_description = "" # Clear after success
    except Exception as e:
        st.error(f"Could not submit to Sheet: {e}")
