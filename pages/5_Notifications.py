import streamlit as st
import json
import os

INVITES_FILE = "invites.json"
TOKEN_FILE = "tokens.json"
PROJECTS_FILE = "projects.json"
NOTIFICATIONS_FILE = "notifications.json"
COMPLAINTS_FILE = "complaints.json"

# ---------- Helper Functions ----------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_invites():
    return load_json(INVITES_FILE, [])

def save_invites(invites):
    save_json(INVITES_FILE, invites)

def load_notifications():
    return load_json(NOTIFICATIONS_FILE, [])

def save_notifications(data):
    save_json(NOTIFICATIONS_FILE, data)

def load_projects():
    return load_json(PROJECTS_FILE, [])

def save_projects(projects):
    save_json(PROJECTS_FILE, projects)

def update_tokens(username, change):
    tokens = load_json(TOKEN_FILE, {})
    tokens[username] = max(0, tokens.get(username, 50) + change)
    save_json(TOKEN_FILE, tokens)

def load_complaints():
    return load_json(COMPLAINTS_FILE, [])

def save_complaints(data):
    save_json(COMPLAINTS_FILE, data)

# ---------- UI Setup ----------
if not st.session_state.get("logged_in") and os.path.exists("auth_cache.json"):
    with open("auth_cache.json", "r") as f:
        data = json.load(f)
        st.session_state.logged_in = data.get("logged_in", False)
        st.session_state.username = data.get("username", "")
        st.session_state.role = data.get("role", "")

user = st.session_state.get("username")
if not user:
    st.error("You must be logged in to view this page.")
    st.stop()

notifications = load_notifications()
user_notifications = [n for n in notifications if n["to"] == user]
show_alert = "🔴 " if user_notifications else ""

st.set_page_config(page_title="Notifications", layout="centered")
st.title(f"{show_alert}Notifications")

# ---------- Notification Section ----------
if user_notifications:
    st.subheader("🔔 Your Notifications")
    for i, note in enumerate(user_notifications):
        st.info(note["message"])
    notifications = [n for n in notifications if n["to"] != user]  # Clear after viewing
    save_notifications(notifications)
else:
    st.write("You have no new notifications.")

# ---------- Rebuttal Submission ----------
complaints = load_complaints()
my_complaints = [c for c in complaints if c.get("about") == user and not c.get("rebuttal")]

if my_complaints:
    st.subheader("📝 Rebuttal Requests")
    for i, comp in enumerate(my_complaints):
        with st.form(f"rebut_form_{i}"):
            st.write(f"You were reported by `{comp['from']}` for: {comp['reason']}")
            rebut = st.text_area("Respond with your rebuttal:", key=f"rebut_text_{i}")
            submit = st.form_submit_button("Submit Rebuttal")
            if submit and rebut.strip():
                comp["rebuttal"] = rebut.strip()
                save_complaints(complaints)
                st.success("Rebuttal submitted.")

# ---------- Invite Section ----------
st.markdown("---")
st.subheader("📨 Incoming Project Invites")
invites = load_invites()
my_invites = [i for i in invites if i["to"] == user and i["status"] == "pending"]

if my_invites:
    for invite in my_invites:
        st.write(f"📁 Invite from **{invite['from']}** to access **Project ID {invite['projectId']}**")
        col1, col2 = st.columns(2)
        if col1.button("✅ Accept", key=f"acc_{invite['projectId']}"):
            invite["status"] = "accepted"
            save_invites(invites)
            st.success("Invite accepted.")
            st.rerun()
        if col2.button("❌ Reject", key=f"rej_{invite['projectId']}"):
            invite["status"] = "rejected"
            update_tokens(invite["from"], -3)  # Penalize inviter
            save_invites(invites)
            st.warning("Invite rejected. 3 tokens deducted from inviter.")
            st.rerun()
else:
    st.info("No new invites at the moment.")

# ---------- Shared Projects Editor ----------
st.markdown("---")
st.subheader("🤝 Collaborate on Shared Projects")

accepted_invites = [i for i in invites if i["to"] == user and i["status"] == "accepted"]
projects = load_projects()

shared_projects = [p for p in projects if any(i["projectId"] == p["id"] for i in accepted_invites)]

if shared_projects:
    selected = st.selectbox("Choose a project to collaborate on:", shared_projects, format_func=lambda x: x["name"])
    content = st.text_area("Edit Content:", value=selected["content"], height=300)
    if st.button("💾 Save Changes", key=f"save_{selected['id']}"):
        for p in projects:
            if p["id"] == selected["id"]:
                p["content"] = content
                break
        save_projects(projects)
        st.success("Project updated successfully.")
else:
    st.info("No shared projects available to edit.")
