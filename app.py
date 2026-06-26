import streamlit as st
import google.generativeai as genai
from google.oauth2 import service_account
import gspread
from PIL import Image
import io

# 1. Setup the AI (Gemini 2.5)
try:
    api_key = "AQ.Ab8RN6JWFIZUB-rscRW-TcseQO4PhWei0JDquHSvZu8XupsIjg"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"Missing Gemini API Setup: {e}")

# 2. Setup Google Sheets Connection
try:
    raw_private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC17KvltXmPRaC9\nT+wMJRXuVhmOLYUpkU3LWVAzqTymeFp4pSGZDrCSuTngT7Gb5aQds9WyRRlUP3Ug\n3PDGAA4hIUEXuycZhDjTojIxLkZg0TP+/o+XcdN28srAvJddDvHOGAc414xo8/vF\n4a5GUGT6J+jGdsW7otVV+p1J0W0U0RFYNJk5VgzwEGJc1ofHAlnyO9NsidCY35X2\n6EoRLUr5MR6ZTcAlDT0p2YRU8OBbQeuTqfIo1BNL6RT/laBk86Zh7DQ1/naIde6T\n1IZNAzv+0CUpI5zST5lGa3PrsON2nuW6KoPjthb+JaYIcCGcQ6M/D3yEhtBOuqNg\nykcdLVCvAgMBAAECggEAVqcUeaWm8QdJOOMInABOIegA5CfqdZIwa9tuyCykJubM\nsQp2pmDI2ho/5wgOoSMQuNUfxHoFRouzTqPuS2FbWYxtZNBQH2dLagKnxaU1AIil\nK6A05P3iq5WZ3ZP2xOyJYJExX3HL/3G3StnkGLnSXxUDWwTXyjgVRY7JvI90VaUx\nvASXM6N201R8olYnDnd6XeEtiCGmEwX8Py6/yxWto5DuNVcG0kUummABxS3f8BQd\n89IIBexl7UN7vGydL/vBqcFTZFcxNdh7u6mO2PpIBrkTMo2SD9R3OOxrGLIfSsiN\nlE0fuVYNcCEWG/fZEt0xi+0POFHF4CjnIIZsXZldgQKBgQDiV8c408Fisl5uSxIf\n/Q7SqiJOzKpYLfCbRhiifuRLEmmYOpDL5HTelGRSiGhN0GWKHuk3CplPPX+XdiGE\ngNstDcW1e/bv0eXI9FahAdxIRpDOflbc7VfYasWUbfPIq09pkBPLkvpYL6oMv/hL\nLPQoy7dfdH8ziiAnYFa+4bEskwKBgQDNwveE8C/v/dT876DmgSOcoC5rOUULmjQB\nE+tZawHPRrWIrjYYyPXJhwka7NCy1onc3TMvLYugz77WXr2CqPnBlTVYfyiL/GvJ\nm4MO3itGHUYUkiAIejyVUOyQltLSIGePWPnR2WlrCnXGLsRLY/l/GXk4LhHcp1pC\ntv26D5y49QKBgBcMvVsKJX15kKhGuNfNG39UmB3SNd64/vGxF70kkvcaLuqzvB8n\nasdn8Td+cLDL8is4rqNOTwKEzsOL4inuPWO/LU0oDKOrim0GhPPsjpRFq2V79DiX\awS9CtXsxJDA8VtcssdedmQYpoaZ3h05vLuS01/DK1kCTff0laDmtvZFAoGBAMkv\nG7MY4dZHGwyhBHK8y+Ql3p0qZu88PCLdph1M+nz/hxn4NJ6xR1lftjBkYn6qNCwH\nADfd0YtP9SlHgwaRT3rO+FTqJ+wPyBhc/Jz579fjYZVVdwqy8i+Q621IeyPHWVqY\nxdNAP8nQdW1sZrPMMbPrZVHgAcj8vM1EfPuCrltNAoGBAIk9NZAw+/fsRftly3+I\nEM3Cc6c1RZyr2CNzxpbvwOfgHtTMTNqGTZmuFjGmAGi3SjIKjwxfjHvJuUxF+5Dp\nmXuuQBAHX5iMa0TL4CqSb+NjOSD9lvGbRkm9R0mRyzL17nIup03vjJ7Ew4AdSfyo\nLwO/Ojmf+lkCP2F41isXuX2o\n-----END PRIVATE KEY-----\n"
    
    # This line forces the text formatting to use proper newlines
    clean_private_key = raw_private_key.replace("\\n", "\n")

    credentials_dict = {
        "type": "service_account",
        "project_id": "mimetic-planet-500614-f2",
        "private_key_id": "0d62eda167cb56b1a9424ac6178daae815fd3d82",
        "private_key": clean_private_key,
        "client_email": "sheets-bot@mimetic-planet-500614-f2.iam.gserviceaccount.com",
        "client_id": "106061085208077860075",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheets-bot%40mimetic-planet-500614-f2.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    creds = service_account.Credentials.from_service_account_info(
        credentials_dict, 
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(creds)
    
    SPREADSHEET_ID = "1Vn4Z-19fZSo-xLiY4juUcCosRxsp4E4vB1nL0Veirms"
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.get_worksheet(0)
except Exception as e:
    st.error(f"Google Sheets connection setup incomplete: {e}")

# 3. The Mobile App Interface
st.set_page_config(page_title="Bates Estates Ledger", page_icon="📸")
st.title("📸 Quick Sale Ledger")
st.write("Snap a pic, enter details, and send it straight to Google Sheets.")

img_file = st.camera_input("Take a photo of the items")
amount = st.text_input("Col B: Amount ($)", value="10")
payment = st.selectbox("Col C: Payment Method", ["Cash", "Venmo", "Check", "Card"])

if st.button("Log Sale & Update Sheet"):
    if img_file is not None:
        if 'worksheet' in globals() or 'worksheet' in locals():
            with st.spinner("AI is itemizing the photo..."):
                try:
                    image_bytes = img_file.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    prompt = "Look at this image of items bought at a sale. Give me a brief, clear, itemized description of the physical objects you see. Do not include prices. Keep it under 8 words."
                    response = model.generate_content([prompt, image])
                    description = response.text.strip()
                    
                    row_to_add = [description, amount, payment]
                    worksheet.append_row(row_to_add, value_input_option="USER_ENTERED")
                    st.success(f"Logged! Row added: {description} | ${amount} | {payment}")
                except Exception as e:
                    st.error(f"Error logging sale: {e}")
        else:
            st.error("Google Sheets connection is broken.")
    else:
        st.warning("Please snap a photo first!")
