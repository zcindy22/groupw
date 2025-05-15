<<<<<<< Updated upstream
import streamlit as st

st.set_page_config(page_title="Paid Editor", layout="wide")

st.title("🔒 Paid User Editor")
st.write("Welcome to the Paid User Editor")

user_text = st.text_area("Enter your text:", height=300)

if st.button("Process Text"):
    word_count = len(user_text.split())
    st.success(f"Processed text with {word_count} words!")
=======
>>>>>>> Stashed changes
