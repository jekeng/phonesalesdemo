import streamlit as st
from datetime import datetime
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
# Define the scope and authenticate with Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets"]


# Load credentials from Streamlit secrets
creds_dict = {
    "type": st.secrets["gcp"]["type"],
    "project_id": st.secrets["gcp"]["project_id"],
    "private_key_id": st.secrets["gcp"]["private_key_id"],
    "private_key": st.secrets["gcp"]["private_key"],
    "client_email": st.secrets["gcp"]["client_email"],
    "client_id": st.secrets["gcp"]["client_id"],
    "auth_uri": st.secrets["gcp"]["auth_uri"],
    "token_uri": st.secrets["gcp"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp"]["client_x509_cert_url"],
    "universe_domain": st.secrets["gcp"]["universe_domain"]
}


client = gspread.authorize(creds_dict)

# Open the Google Sheet by name
sheet = client.open("Phone Sales Tracker").sheet1  # Replace with your sheet name

# --- Initialize Session State ---
if 'stats' not in st.session_state:
    st.session_state.stats = {
        "Dials": 0,
        "Picked Up": 0,
        "No Booked Meeting": 0,
        "Booked Meeting": 0
    }

if 'log' not in st.session_state:
    st.session_state.log = []

# --- Streamlit App Interface ---
st.title("📞 Phone Sales Tracker")

# Outcome selection
outcome = st.selectbox("Select Call Outcome:", [
    "Dial",
    "Picked Up",
    "No Booked Meeting",
    "Booked Meeting"
])

# Record button
if st.button("Record Outcome"):
    st.session_state.stats["Dials"] += 1  # Always increment Dials

    if outcome == "Picked Up":
        st.session_state.stats["Picked Up"] += 1
    elif outcome == "No Booked Meeting":
        st.session_state.stats["Picked Up"] += 1
        st.session_state.stats["No Booked Meeting"] += 1
    elif outcome == "Booked Meeting":
        st.session_state.stats["Picked Up"] += 1
        st.session_state.stats["Booked Meeting"] += 1

    # Log the outcome with timestamp
    st.session_state.log.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Outcome": outcome
    })

    st.success(f"Recorded: {outcome}")

# Display statistics
st.header("📊 Call Stats")
st.write(pd.DataFrame([st.session_state.stats]))

# Display full log
st.header("📝 Call Log")
st.dataframe(pd.DataFrame(st.session_state.log))

# --- Update Google Sheets ---
if st.button("Save to Google Sheets"):
    try:
        today_date = datetime.today().strftime('%Y-%m-%d')
        new_entry = [
            today_date,
            st.session_state.stats["Dials"],
            st.session_state.stats["Picked Up"],
            st.session_state.stats["No Booked Meeting"],
            st.session_state.stats["Booked Meeting"]
        ]

        all_rows = sheet.get_all_values()
        row_index = None

        # Check if today's date exists in the sheet
        for idx, row in enumerate(all_rows):
            if row and row[0] == today_date:
                row_index = idx + 1  # gspread uses 1-based indexing
                break

        if row_index:
            # Update existing row
            cell_range = f"A{row_index}:E{row_index}"
            sheet.update(cell_range, [new_entry])
            st.info("Today's stats updated in Google Sheets.")
        else:
            # Append new row
            sheet.append_row(new_entry)
            st.info("New day added to Google Sheets.")

    except Exception as e:
        st.error(f"Failed to update Google Sheets: {e}")
