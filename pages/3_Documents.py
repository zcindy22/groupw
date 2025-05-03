import streamlit as st
import requests

API_URL = "http://localhost:5000/api"

st.set_page_config(page_title="Load Document", layout="centered")
st.title("📂 Load a Previous Document")

# Check for login
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access your documents.")
    st.stop()

username = st.session_state.get("username", "")
user_text = st.session_state.get("user_text", "")

# Fetch user's documents from the backend
response = requests.get(f"{API_URL}/documents/{username}")
if response.status_code != 200:
    st.error("Failed to retrieve documents.")
    st.stop()

documents = response.json()
if not documents:
    st.info("You have no saved documents yet.")
    st.stop()

# Select document
selected_doc = st.selectbox("Select a document to load:", documents, format_func=lambda doc: doc['title'])

# Click to load
if st.button("📥 Load into Editor"):
    """doc_id = selected_doc['id']
    doc_response = requests.get(f"{API_URL}/document/{doc_id}")
    if doc_response.status_code != 200:
        st.error("Failed to load document content.")
        st.stop()"""

    """content_to_load = doc_response.json().get("content", "")"""

    # Check if there's already text in the editor
    if user_text.strip():
        """st.session_state.pending_doc_content = content_to_load"""
        st.session_state.confirm_load = True
        st.warning("⚠️ You already have content in the editor. Do you want to overwrite it?")
    else:
        """st.session_state.user_text = content_to_load"""
        st.success("✅ Document loaded into editor.")

# Confirm overwrite
if st.session_state.get("confirm_load", False):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, overwrite editor content"):
            st.session_state.user_text = st.session_state.pending_doc_content
            st.session_state.pending_doc_content = ""
            st.session_state.confirm_load = False
            st.success("✅ Document loaded into editor.")
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.pending_doc_content = ""
            st.session_state.confirm_load = False
            st.info("Cancelled. Your editor content is unchanged.")
