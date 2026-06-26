import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
import gspread
from PIL import Image
import io

# 1. Setup the AI (Gemini)
# We safely pull this from Streamlit's hidden secrets manager
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Missing Gemini API Key. Please add it to Streamlit Secrets.")

# 2. Setup Google Sheets Connection
# We safely connect using standard Streamlit Google Sheets integration
try:
    import json
credentials_dict = json.loads(st.secrets["gspread_credentials"])
    
    # Your specific Sheet ID
    SPREADSHEET_ID = "1Vn4Z-19fZSo-xLiY4juUcCosRxsp4E4vB1nL0Veirms"
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.get_worksheet(0) # First sheet tab
except Exception as e:
    st.error(f"Google Sheets connection setup incomplete: {e}")

# 3. The Mobile App Interface
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸")
st.title("📸 Quick Sale Ledger")
st.write("Snap a pic, enter details, and send it straight to Google Sheets.")

# Sale Inputs
img_file = st.camera_input("Take a photo of the items") # Opens mobile camera
amount = st.text_input("Col B: Amount ($)", value="10")
payment = st.selectbox("Col C: Payment Method", ["Cash", "Venmo", "Check", "Card"])

if st.button("Log Sale & Update Sheet"):
    if img_file is not None:
        with st.spinner("AI is itemizing the photo..."):
            try:
                # Read the camera image
                image_bytes = img_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Ask AI to describe the items in the picture
                prompt = "Look at this image of items bought at a sale. Give me a brief, clear, itemized description of the physical objects you see. Do not include prices. Keep it under 8 words."
                response = model.generate_content([prompt, image])
                description = response.text.strip()
                
                # Prepare the row data
                row_to_add = [description, amount, payment]
                
                # Send it to Google Sheets
                worksheet.append_row(row_to_add, value_input_option="USER_ENTERED")
                st.success(f"Logged! Row added: {description} | ${amount} | {payment}")
            except Exception as e:
                st.error(f"Error logging sale: {e}")
    else:
        st.warning("Please snap a photo first!")
