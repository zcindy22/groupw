import streamlit as st
from supabase_proj.db_utils import get_user_documents, submit_complaint_by_email

st.set_page_config(page_title="Complaints", layout="centered")
st.title("📣 File a Complaint")

if not st.session_state.get("logged_in"):
    st.warning("Please log in to file a complaint.")
    st.stop()

user_id = st.session_state.get("id")
if not user_id:
    st.error("User ID not found in session.")
    st.stop()

my_docs = get_user_documents(user_id)
doc_options = {doc["docname"]: doc["id"] for doc in my_docs}

st.subheader("Submit a Complaint")
with st.form("complaint_form"):
    accused_email = st.text_input("Accused User's Email")
    text_choice = st.selectbox("Select Related Document", list(doc_options.keys()))
    reason = st.text_area("Describe the Issue")
    submit = st.form_submit_button("Submit Complaint")

    if submit:
        if not accused_email or not reason:
            st.warning("All fields must be filled.")
        else:
            try:
                submit_complaint_by_email(
                    complainer_id=user_id,
                    accused_email=accused_email,
                    text_id=doc_options[text_choice],
                    reason=reason
                )
                st.success("Complaint submitted successfully.")
            except Exception as e:
                st.error(f"Failed to submit complaint: {e}")
