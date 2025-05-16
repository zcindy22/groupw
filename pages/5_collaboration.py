import streamlit as st
from supabase_proj.db_utils import (
    get_incoming_collab_requests,
    get_outgoing_collab_requests,
    respond_to_request,
    get_text_title,
    get_user_data_by_email,
    send_collab_request,
    get_user_documents
)

st.set_page_config(page_title="Collaboration Requests", layout="centered")
st.title("🤝 Collaboration Requests")

#  Complaints 
st.markdown("---")
if st.button("📣 Submit a Complaint"):
    st.switch_page("pages/6_Complaints.py")  


if not st.session_state.get("logged_in"):
    st.warning("Please log in to access collaboration features.")
    st.stop()

user_id = st.session_state.get("id")
if not user_id:
    st.error("User ID not found. Please log in again.")
    st.stop()

st.subheader("📨 Send Collaboration Request")

# Load user's documents to select from
my_docs = get_user_documents(user_id)
docname_to_id = {doc['docname']: doc['id'] for doc in my_docs}

if not docname_to_id:
    st.info("You have no documents to share.")
else:
    selected_docname = st.selectbox("Select a document to share", list(docname_to_id.keys()))
    invitee_email = st.text_input("Enter the email of the user you want to invite")

    if st.button("Send Request"):
        invitee_profile = get_user_data_by_email(invitee_email)
        if not invitee_profile:
            st.error("User with this email does not exist.")
        else:
            send_collab_request(
                inviter_id=user_id,
                invitee_id=invitee_profile["id"],
                text_id=docname_to_id[selected_docname]
            )
            st.success(f"Collaboration request sent to {invitee_email} for '{selected_docname}'")

#   Requests from 
st.subheader("📥 Collaboration Requests")
incoming = get_incoming_collab_requests(user_id)
if not incoming:
    st.info("No incoming requests.")
else:
    for req in incoming:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(f"**From:** `{req['inviter_id']}`  |  **Document:** `{get_text_title(req['text_id'])}`")
        with col2:
            if st.button("✅ Accept", key=f"accept_{req['id']}"):
                respond_to_request(req['id'], "accepted")
                st.success("Request accepted.")
                st.rerun()
            if st.button("❌ Reject", key=f"reject_{req['id']}"):
                respond_to_request(req['id'], "rejected")
                st.warning("Request rejected.")
                st.rerun()

# Outgoing Requests the requests that the user has sent
st.markdown("---")
st.subheader("📤 Sent Collaboration Requests")
outgoing = get_outgoing_collab_requests(user_id)
if not outgoing:
    st.info("You haven't sent any collaboration requests.")
else:
    for req in outgoing:
        st.markdown(f"📨 To: `{req['invitee_id']}`  |  **Document:** `{get_text_title(req['text_id'])}`  |  **Status:** `{req['status']}`")

