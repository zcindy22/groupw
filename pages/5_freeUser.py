import streamlit as st
from supabase_proj.db_utils import suspend_user
import time
import re
import sys
import os

# Make supabase_proj accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from supabase_proj.db_utils import get_blacklist, suggest_blacklist_word

st.set_page_config(page_title="Free Editor", layout="centered")
st.title("Free User Editor")

if 'logged_in' not in st.session_state:
    st.error("Please log in first!")
    st.stop()

if st.session_state.status == "suspended":
    st.error("Your account is suspended for 3 minutes due to word limit violation.")
    st.stop()

if st.session_state.role != "free":
    st.error("Please use the paid user editor!")
    st.stop()

#  Input method 
input_type = st.radio("Choose input method:", ["Text Box", "Upload .txt File"])
user_text = ""

if input_type == "Text Box":
    user_text = st.text_area("Enter your text (max 20 words)", height=150)
else:
    uploaded_file = st.file_uploader("Upload a .txt file - **You can upload only text files**", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
        st.text_area("File content (read-only)", user_text, height=150, disabled=True)

#  Submit button logic 
if st.button("Submit"):
    word_list = re.findall(r'\b\w+\b', user_text.strip())
    word_count = len(word_list)

    if word_count > 20:
        suspend_user()
        st.error("You entered more than 20 words. You are suspended for 3 minutes.")
    elif word_count == 0:
        st.warning("Please enter some text.")

    elif all(not word.isalpha() for word in word_list):
        st.warning("Please enter meaningful text.")
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
            st.text(str(e))  

#  Suggest a word to be blacklisted 
st.markdown("---")
st.subheader("Suggest a word for the blacklist")

suggested_word = st.text_input("Enter a word you think should be blacklisted:")

if st.button("Submit Suggestion"):
    if not suggested_word.strip():
        st.warning("Please enter a valid word.")
    
    elif " " in suggested_word:
        st.warning("Please enter a single word without spaces.")

    elif not suggested_word.isalpha():
        st.warning("Please enter a valid word without special characters or numbers.")
    else:
        try:
            suggest_blacklist_word(suggested_word.lower())
            st.success("Thank you! Your suggestion has been submitted for review.")
        except Exception as e:
            error_msg = str(e)
            if "duplicate key value" in error_msg:
                st.warning("This word has already been submitted.")
            else:
                st.error("Failed to submit the word. Please try again later.")
                st.text(error_msg)  
