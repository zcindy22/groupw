import streamlit as st
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supabase_proj.db_utils import get_blacklist

st.set_page_config(page_title="Free Editor", layout="centered")
st.title("Free User Editor")

# --- Suspension timer setup ---
if "suspended_until" not in st.session_state:
    st.session_state.suspended_until = 0

now = time.time()
if now < st.session_state.suspended_until:
    st.error("Your account is suspended for 3 minutes due to word limit violation.")
    st.stop()

# --- Input method ---
input_type = st.radio("Choose input method:", ["Text Box", "Upload .txt File"])
user_text = ""

if input_type == "Text Box":
    user_text = st.text_area("Enter your text (max 20 words)", height=150)
else:
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
        st.text_area("File content (read-only)", user_text, height=150, disabled=True)

# --- Submit button logic ---
if st.button("Submit"):
    word_list = user_text.strip().split()
    word_count = len(word_list)

    if word_count > 20:
        st.session_state.suspended_until = now + 180
        st.error("You entered more than 20 words. You are suspended for 3 minutes.")
    elif word_count == 0:
        st.warning("Please enter some text.")
    else:
        try:
            blacklist = get_blacklist()
            filtered_words = [
                "*" * len(word) if word.lower() in blacklist else word
                for word in word_list
            ]
            filtered_text = " ".join(filtered_words)
            st.success("Blacklisted words were filtered. You may correct the result below.")
            st.text_area("Self-correction (editable):", value=filtered_text, height=150)
        except Exception as e:
            st.error("Could not connect to backend.")
