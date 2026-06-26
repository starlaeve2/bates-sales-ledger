import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io
from datetime import datetime

# Stately mobile layout settings
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

# 1. Setup the AI
api_key = "AQ.Ab8RN6I25LS1VwayxsGJKf_lGU4DAZ7pCSP1417jdWC4S5AEqg"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Gemini Setup Error: {e}")

# 2. Initialize session storage
if "ledger_data" not in st.session_state:
    st.session_state.ledger_data = []
if "temp_description" not in st.session_state:
    st.session_state.temp_description = ""

# App Header
st.title("📸 Quick Sale Ledger")
st.write("Snap a pic, edit the items, and log it.")
st.write("---")

# Camera Input
img_file = st.camera_input("Take a photo of the items")

if img_file is not None:
    # Only run AI if we haven't generated a description for this photo yet
    if st.session_state.temp_description == "":
        with st.spinner("AI is itemizing the photo..."):
            try:
                image_bytes = img_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Updated prompt for a clean, comma-separated list
                prompt = "List the main physical items in this image as a comma-separated list. Do not include descriptions of people, hands, or actions. Just the items."
                response = model.generate_content([prompt, image])
                st.session_state.temp_description = response.text.strip()
            except Exception as e:
                st.error(f"Error: {e}")

    # Display editable fields for the user to approve/change
    st.subheader("Confirm Details")
    edited_description = st.text_input("Item Description:", value=st.session_state.temp_description)
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.text_input("Amount ($)", value="10")
    with col2:
        payment = st.selectbox("Payment Method", ["Cash", "Venmo", "Check", "Card"])

    # Final "Log" button
    if st.button("Confirm & Log to Ledger", use_container_width=True):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {
            "Timestamp": current_time,
            "Item Description": edited_description,
            "Amount ($)": amount,
            "Payment Method": payment
        }
        st.session_state.ledger_data.append(new_row)
        st.success(f"Logged: {edited_description}")
        # Reset for next item
        st.session_state.temp_description = ""
        st.rerun()

# Display Table
if st.session_state.ledger_data:
    st.write("---")
    st.subheader("Today's Logged Sales")
    df = pd.DataFrame(st.session_state.ledger_data)
    st.table(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Finished Spreadsheet (.csv)", csv, "sales_ledger.csv", "text/csv")
