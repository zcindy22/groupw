import streamlit as st
from supabase_proj.db_utils import get_collaborations, accept_collaboration, reject_collaboration
from supabase_proj.db_utils import show_complains, dismiss_complains, show_against_complains, dismiss_against_complains

# Sample data for the session (replace this with your DB query later)
if "collab_requests" not in st.session_state:
    st.session_state.collab_requests = None


if "accepted_collaboration_id" not in st.session_state:
    st.session_state.accepted_collaboration_id = None

if "complaint_updates" not in st.session_state:
    st.session_state.complaint_updates = None


if "complaints_against_user" not in st.session_state:
    st.session_state.complaints_against_user = None

st.title("Notifications Dashboard")

if "logged_in" not in st.session_state:
    st.error("Please log in first!")
    st.stop()

# === Collaboration Requests Section ===
st.header("Collaboration Requests")

get_collaborations()
show_complains()
show_against_complains()

if st.session_state.get("collab_requests"):
    for req in st.session_state.collab_requests:
        with st.expander(f"Request from {req.get('inviter_email', 'Unknown')}"):
            st.write(f"Document: **{req.get('docname', 'Unnamed Document')}**")

            col1, col2 = st.columns([1, 1])

            if col1.button("✅ Accept", key=f"accept_{req['collaboration_id']}"):
                st.session_state.accepted_collaboration_id = req["collaboration_id"]
                accept_collaboration()
                st.success(f"Marked request from {req.get('inviter_email', 'Unknown')} for acceptance")
                st.rerun()

            if col2.button("❌ Reject", key=f"reject_{req['collaboration_id']}"):
                st.session_state.accepted_collaboration_id = req["collaboration_id"]
                reject_collaboration()
                st.warning(f"Rejected request from {req.get('inviter_email', 'Unknown')}")
                st.rerun()
else:
    st.info("No pending collaboration requests.")


# === Complaint Notifications Section ===
st.header("Complaint Status Updates")

if st.session_state.complaint_updates:
    for complaint in st.session_state.complaint_updates:
        st.write(f"**Reason:** {complaint.get("reason", "No message provided.")}")
        if st.button("Dismiss", key=f"dismiss_{complaint['id']}"):
            dismiss_complains(complaint["id"])
            st.session_state.complaint_updates = [
                c for c in st.session_state.complaint_updates if c["id"] != complaint["id"]
            ]
            st.rerun()
else:
    st.success("Nothing to see here.")

st.header("Complaints Against You")
if st.session_state.complaints_against_user:
    for complaint in st.session_state.complaints_against_user:
        with st.container():
            st.markdown(f"**Reviewed by**: {complaint.get('reviewed_by', 'Unknown')}  \n**Reason**: {complaint.get('message', 'No message')}")
            #st.write(complaint.get("reason", "No message provided."))
            if st.button("Dismiss", key=f"dismiss_against_{complaint['id']}"):
                dismiss_against_complains(complaint["id"])
                st.session_state.complaints_against_user = [
                    c for c in st.session_state.complaints_against_user if c["id"] != complaint["id"]
                ]
                st.rerun()
else:
    st.success("No complaints filed against you.")