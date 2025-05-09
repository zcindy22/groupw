import streamlit as st
import requests
import time

st.set_page_config(page_title="Free Editor", layout="centered")
st.title("Free User Editor")

# --- Session state setup for suspension timer ---
if "suspended_until" not in st.session_state:
    st.session_state.suspended_until = 0

# --- Suspension check ---
now = time.time()
if now < st.session_state.suspended_until:
    remaining = int(st.session_state.suspended_until - now)
    st.error(f"You are suspended for exceeding 20 words. Try again in {remaining} seconds.")
    st.stop()

# --- Input: Text box or file upload ---
input_type = st.radio("Choose input method:", ["Text Box", "Upload .txt File"])

user_text = ""

if input_type == "Text Box":
    user_text = st.text_area("Enter your text (max 20 words)", height=150)
else:
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
        st.text_area("File content (read-only)", user_text, height=150, disabled=True)

# --- Actions: Submit Text ---
if st.button("Submit"):
    word_count = len(user_text.strip().split())

    if word_count > 20:
        st.session_state.suspended_until = now + 180  # suspend for 3 minutes
        st.error("You entered more than 20 words. You are suspended for 3 minutes.")
    elif word_count == 0:
        st.warning("Please enter some text.")
    else:
        try:
            res = requests.post("http://localhost:8000/api/free/submit", json={"text": user_text})
            if res.status_code == 200:
                filtered_text = res.json().get("filtered_text", "")
                st.success("Text submitted successfully. Blacklisted words were filtered.")
                st.text_area("Edit your corrected version here:", value=filtered_text, height=150)
            else:
                st.error("Submission failed. Please try again.")
        except:
            st.error("Could not connect to backend server.")


