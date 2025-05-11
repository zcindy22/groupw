import streamlit as st
import json
import os
from io import BytesIO

st.set_page_config(page_title="Documents", layout="centered")
st.title("📂 My Documents")

# ---------- Restore login from cache if needed ----------
if not st.session_state.get("logged_in") and os.path.exists("auth_cache.json"):
    with open("auth_cache.json", "r") as f:
        data = json.load(f)
        st.session_state.logged_in = data.get("logged_in", False)
        st.session_state.username = data.get("username", "")
        st.session_state.role = data.get("role", "")

if not st.session_state.get("logged_in"):
    st.warning("Please log in first to access your documents.")
    st.stop()

# ---------- File paths ----------
PROJECTS_FILE = "projects.json"
INVITES_FILE = "invites.json"
TOKEN_FILE = "tokens.json"

# ---------- Utility functions ----------
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

def load_invites():
    return load_json(INVITES_FILE, [])

def save_invites(invites):
    save_json(INVITES_FILE, invites)

def get_tokens(username):
    tokens = load_json(TOKEN_FILE, {})
    return tokens.get(username, 50)

def update_tokens(username, change):
    tokens = load_json(TOKEN_FILE, {})
    tokens[username] = max(0, tokens.get(username, 50) + change)
    save_json(TOKEN_FILE, tokens)
    st.session_state.tokens = tokens[username]

# ---------- Session ----------
username = st.session_state.get("username")
is_paid_user = st.session_state.get("role") == "paid"

# ---------- My Projects ----------
st.subheader("📁 My Saved Projects")
projects = load_projects()
my_projects = [p for p in projects if p.get("owner") == username]

if my_projects:
    for project in my_projects:
        with st.expander(project["name"]):
            st.code(project["content"])
            share_to = st.text_input(f"Share '{project['name']}' with:", key=f"share_{project['id']}")
            if st.button("Share", key=f"btn_{project['id']}"):
                if share_to and share_to not in project["sharedWith"]:
                    project["sharedWith"].append(share_to)
                    save_projects(projects)
                    invites = load_invites()
                    invites.append({
                        "from": username,
                        "to": share_to,
                        "projectId": project["id"],
                        "status": "pending"
                    })
                    save_invites(invites)
                    st.success(f"Shared with {share_to}")

            # ---------- Download Button ----------
            if is_paid_user:
                file_content = project["content"]
                file_bytes = BytesIO(file_content.encode("utf-8"))
                filename = f"{project['name'].replace(' ', '_')}.txt"

                if st.download_button("⬇️ Download as .txt", file_bytes, file_name=filename, mime="text/plain", key=f"dl_{project['id']}"):
                    if get_tokens(username) >= 5:
                        update_tokens(username, -5)
                        st.success(f"Downloaded '{filename}' and deducted 5 tokens.")
                else:
                    st.error("Not enough tokens to download.")
            else:
                st.info("Upgrade to a paid account to download projects.")
else:
    st.info("You have no saved projects.")

# ---------- Shared Projects ----------
st.markdown("---")
st.subheader("📬 Projects Shared With Me")
shared_to_me = [p for p in projects if username in p.get("sharedWith", [])]

if shared_to_me:
    for p in shared_to_me:
        st.write(f"**{p['name']}**")
        st.code(p["content"])
else:
    st.info("No projects shared with you yet.")