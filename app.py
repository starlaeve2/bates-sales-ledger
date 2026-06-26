import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import io
from datetime import datetime

# Stately mobile layout settings
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸", layout="centered")

# 1. Setup the AI (Gemini 2.5) directly
api_key = "AQ.Ab8RN6JWFIZUB-rscRW-TcseQO4PhWei0JDquHSvZu8XupsIjg"
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Gemini Setup Error: {e}")

# 2. Initialize our local session storage so the app remembers rows while open
if "ledger_data" not in st.session_state:
    st.session_state.ledger_data = []

# App Header
st.title("📸 Quick Sale Ledger")
st.write("Snap a pic, enter details, and download your spreadsheet at the end of the day.")
st.write("---")

# Camera & Data Input Section
img_file = st.camera_input("Take a photo of the items")

# Side-by-side inputs for cleaner mobile layout
col1, col2 = st.columns(2)
with col1:
    amount = st.text_input("Amount ($)", value="10")
with col2:
    payment = st.selectbox("Payment Method", ["Cash", "Venmo", "Check", "Card"])

# Log Sale Button
if st.button("Log Sale to Local Ledger", use_container_width=True):
    if img_file is not None:
        with st.spinner("AI is itemizing the photo..."):
            try:
                # Process Image for AI
                image_bytes = img_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Ask Gemini for the description
                prompt = "Look at this image of items bought at a sale. Give me a brief, clear, itemized description of the physical objects you see. Do not include prices. Keep it under 8 words."
                response = model.generate_content([prompt, image])
                description = response.text.strip()
                
                # Create a timestamp
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save data directly to the app's internal running memory list
                new_row = {
                    "Timestamp": current_time,
                    "Item Description": description,
                    "Amount ($)": amount,
                    "Payment Method": payment
                }
                st.session_state.ledger_data.append(new_row)
                st.success(f"Added: {description} | ${amount}")
                
            except Exception as e:
                st.error(f"Error processing item: {e}")
    else:
        st.warning("Please snap a photo first!")

st.write("---")

# 3. Running Data Sheet View & Download Block
if st.session_state.ledger_data:
    st.subheader("📋 Today's Logged Sales")
    
    # Convert memory list to a clean visual table
    df = pd.DataFrame(st.session_state.ledger_data)
    st.dataframe(df, use_container_width=True)
    
    # Convert table to standard Excel/CSV data format for downloading
    csv_data = df.to_csv(index=False).encode('utf-8')
    
    # Big friendly download button
    st.download_button(
        label="📥 Download Finished Spreadsheet (.csv)",
        data=csv_data,
        file_name=f"bates_estates_ledger_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Clear Memory Option
    if st.button("Clear App Memory / Start New Day"):
        st.session_state.ledger_data = []
        st.rerun()
else:
    st.info("No items logged yet. Your ledger table will show up here as soon as you save your first item!")
