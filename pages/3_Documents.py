import streamlit as st
from io import BytesIO
import sys, os

# Supabase helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from supabase_proj.db_utils import (
    get_user_documents,
    get_shared_documents,
    get_tokens,
    update_tokens
)

st.set_page_config(page_title="Documents", layout="centered")
st.title("📂 My Documents")


if not st.session_state.get("logged_in"):
    st.warning("Please log in first to access your documents.")
    st.stop()


username = st.session_state.get("email")
is_paid_user = st.session_state.get("role") == "paid"

user_id = st.session_state.get("id")
if not user_id:
    st.error("User ID not found. Please log in again.")
    st.stop()

#  Data Loading
my_projects = get_user_documents(user_id)
shared_docs = get_shared_documents(user_id)
tokens = get_tokens(user_id) if is_paid_user else None

#  Top Stats to see the user's usage
st.markdown("### 📊 Usage Summary")
st.markdown(f"- **Username:** `{username}`")
st.markdown(f"- **Documents Created:** `{len(my_projects)}`")
st.markdown(f"- **Documents Shared With You:** `{len(shared_docs)}`")
if is_paid_user:
    st.markdown(f"- **Tokens Available:** `{tokens}`")
else:
    st.info("Upgrade to a paid account to see and use tokens.")

# My Documents 
st.subheader("📁 My Saved Documents")
if not my_projects:
    st.info("You have no saved documents.")
else:
    for doc in my_projects:
        with st.expander(f"📝 Created: {doc['created_at']}"):
            st.code(doc["content"], language="text")

            # Download logic 
            if is_paid_user:
                file_bytes = BytesIO(doc["content"].encode("utf-8"))
                filename = f"document_{doc['id']}.txt"
                if st.download_button("⬇️ Download", file_bytes, file_name=filename, mime="text/plain", key=f"dl_{doc['id']}"):
                    if tokens >= 5:
                        update_tokens(user_id, -5)
                        st.success(f"Downloaded '{filename}'. 5 tokens deducted.") #deduct tokens
                        tokens -= 5
                    else:
                        st.error("Not enough tokens to download.")
            else:
                st.info("Upgrade to a paid account to download documents.")

#  Shared Documents 
st.markdown("---")
st.subheader("🤝 Documents Shared With Me")
if not shared_docs:
    st.info("No documents shared with you.")
#
else:
    for i, doc in enumerate(shared_docs):
        with st.expander(f"📝 {doc['docname']} (Created: {doc['created_at']})"):
            edited_text = st.text_area("Edit shared content", doc["content"], height=200, key=f"edit_shared_{i}")
            if st.button("Save Changes", key=f"save_shared_{i}"):
                st.warning("Saving shared edits is not yet implemented.")


