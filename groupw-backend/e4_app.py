import streamlit as st
import json
import os

# -------------------- Persistence Setup --------------------
PROJECTS_FILE = "projects.json"
TOKEN_FILE = "tokens.json"
INVITES_FILE = "invites.json"
COMPLAINTS_FILE = "complaints.json"
USERS_FILE = "users.json"  # Shared user data file

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_projects():
    return load_json(PROJECTS_FILE, [])

def save_projects(projects):
    save_json(PROJECTS_FILE, projects)

def load_all_tokens():
    return load_json(TOKEN_FILE, {})

def save_all_tokens(tokens):
    save_json(TOKEN_FILE, tokens)

def get_user():
    return st.session_state.get("username")

def get_tokens(username):
    all_tokens = load_all_tokens()
    return all_tokens.get(username, 50)

def update_tokens(username, change):
    all_tokens = load_all_tokens()
    all_tokens[username] = max(0, all_tokens.get(username, 50) + change)
    save_all_tokens(all_tokens)
    st.session_state.tokens = all_tokens[username]

def load_invites():
    return load_json(INVITES_FILE, [])

def save_invites(invites):
    save_json(INVITES_FILE, invites)

def load_complaints():
    return load_json(COMPLAINTS_FILE, [])

def save_complaints(complaints):
    save_json(COMPLAINTS_FILE, complaints)

# -------------------- UI Layout --------------------
st.title("LLM Editor – E4 File Management")

user = get_user()
if not user:
    st.error("You must be logged in to use this feature.")
    st.stop()

if "tokens" not in st.session_state:
    st.session_state.tokens = get_tokens(user)

st.markdown(f"**Logged in as:** `{user}`  ")
st.markdown(f"**Tokens:** {st.session_state.tokens}")

# -------------------- Save Project Form --------------------
st.subheader("Save New Project")
with st.form("save_form"):
    file_name = st.text_input("Project Name")
    file_content = st.text_area("Text Content")
    save_btn = st.form_submit_button("Save")

if save_btn and st.session_state.tokens >= 5:
    projects = load_projects()
    new_project = {
        "id": len(projects) + 1,
        "name": file_name,
        "content": file_content,
        "owner": user,
        "sharedWith": [],
    }
    projects.append(new_project)
    save_projects(projects)
    update_tokens(user, -5)
    st.success(f"Saved '{file_name}' and used 5 tokens.")
    st.rerun()
elif save_btn:
    st.error("Not enough tokens to save a file.")

# -------------------- My Projects --------------------
st.subheader("My Projects")
projects = load_projects()
for project in projects:
    if project.get("owner") == user:
        with st.expander(project["name"]):
            st.code(project["content"])
            share_to = st.text_input(f"Share '{project['name']}' with: ", key=f"share_{project['id']}")
            if st.button("Share", key=f"btn_{project['id']}"):
                if share_to not in project["sharedWith"]:
                    project["sharedWith"].append(share_to)
                    save_projects(projects)
                    invites = load_invites()
                    invites.append({"from": user, "to": share_to, "projectId": project["id"], "status": "pending"})
                    save_invites(invites)
                    st.success(f"Shared with {share_to}")

# -------------------- Shared With Me --------------------
st.subheader("Shared With Me")
shared_to_me = [p for p in projects if user in p.get("sharedWith", [])]

if shared_to_me:
    for p in shared_to_me:
        st.write(f"**{p['name']}**")
        st.code(p["content"])
else:
    st.info("No projects shared with you yet.")

# -------------------- Invite Management --------------------
st.subheader("Invites Sent To Me")
invites = load_invites()
my_invites = [i for i in invites if i["to"] == user and i["status"] == "pending"]

if my_invites:
    for invite in my_invites:
        st.write(f"Invite from {invite['from']} to access project ID {invite['projectId']}")
        col1, col2 = st.columns(2)
        if col1.button("Accept", key=f"acc_{invite['projectId']}"):
            invite["status"] = "accepted"
            save_invites(invites)
            st.success("Invite accepted")
            st.rerun()
        if col2.button("Reject", key=f"rej_{invite['projectId']}"):
            invite["status"] = "rejected"
            update_tokens(user, -3)
            save_invites(invites)
            st.warning("Invite rejected. 3 tokens deducted from inviter (simulated).")
            st.rerun()
else:
    st.info("No new invites.")

# -------------------- File a Complaint --------------------
st.subheader("File a Complaint")
with st.form("complaint_form"):
    complaint_user = st.text_input("Who are you reporting?")
    complaint_reason = st.text_area("Why are you reporting them?")
    submit_complaint = st.form_submit_button("Submit Complaint")

if submit_complaint:
    complaints = load_complaints()
    complaints.append({"from": user, "about": complaint_user, "reason": complaint_reason})
    save_complaints(complaints)
    st.success("Complaint submitted. A super-user will review it.")
