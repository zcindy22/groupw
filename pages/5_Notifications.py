import streamlit as st

# Sample data for the session (replace this with your DB query later)
if "collab_requests" not in st.session_state:
    st.session_state.collab_requests = [
        {"id": 1, "from": "Alice", "doc": "Project Proposal"},
        {"id": 2, "from": "Bob", "doc": "Research Outline"},
    ]

if "complaint_updates" not in st.session_state:
    st.session_state.complaint_updates = [
        {"id": 1, "message": "Your complaint #456 has been resolved."},
        {"id": 2, "message": "Complaint #789 is under review."},
    ]

st.title("📬 Notifications Dashboard")

# === Collaboration Requests Section ===
st.header("🤝 Collaboration Requests")

if st.session_state.collab_requests:
    for req in st.session_state.collab_requests:
        with st.expander(f"Request from {req['from']}"):
            st.write(f"Document: **{req['doc']}**")
            col1, col2 = st.columns([1, 1])
            if col1.button(f"✅ Accept", key=f"accept_{req['id']}"):
                st.session_state.collab_requests = [r for r in st.session_state.collab_requests if r["id"] != req["id"]]
                st.success(f"Accepted request from {req['from']}")
                st.rerun()

            if col2.button(f"❌ Reject", key=f"reject_{req['id']}"):
                st.session_state.collab_requests = [r for r in st.session_state.collab_requests if r["id"] != req["id"]]
                st.warning(f"Rejected request from {req['from']}")
                st.rerun()
else:
    st.info("No pending collaboration requests.")

# === Complaint Notifications Section ===
st.header("📣 Complaint Status Updates")

if st.session_state.complaint_updates:
    for update in st.session_state.complaint_updates:
        with st.container():
            st.write(update["message"])
            if st.button("Dismiss", key=f"dismiss_{update['id']}"):
                st.session_state.complaint_updates = [c for c in st.session_state.complaint_updates if c["id"] != update["id"]]
                st.rerun()
else:
    st.success("No new complaint updates.")

