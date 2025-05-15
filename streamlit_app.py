import streamlit as st
import re
import json
import os

#if 'logged_in' not in st.session_state:
#    st.session_state.logged_in = False
#if 'username' not in st.session_state:
#    st.session_state.username = None
#if 'user_id' not in st.session_state:
#    st.session_state.user_id = None

st.set_page_config(
    page_title="TextAide – Your AI Workspace",
    page_icon="🧠",
    layout="wide"
)

st.title("TextAide")

# ---------- Restore Login from File ----------
if os.path.exists("auth_cache.json"):
    with open("auth_cache.json", "r") as f:
        data = json.load(f)
        st.session_state.logged_in = data.get("logged_in", False)
        st.session_state.username = data.get("username", "")

# ---------- Abort if not logged in ----------
if not st.session_state.get("logged_in"):
    st.warning("Please log in first from the Login page.")
    st.stop()

# ---------- Setup ----------
if 'user_text' not in st.session_state:
    st.session_state.user_text = ""

word_limit = 500
current_word_count = len(re.findall(r'\b\w+\b', st.session_state.user_text))

# ---------- Text Editor UI ----------
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"**Word Limit:** {word_limit} | **Current Words:** {current_word_count}")
    st.session_state.user_text = st.text_area("Enter your text below", value=st.session_state.user_text, height=400)

words_to_highlight = ['text', 'Streamlit', 'highlight']
replacement_words = {'text': 'document', 'Streamlit': 'WebApp', 'highlight': 'emphasize'}

def get_word_occurrences(text, words):
    occurrences = []
    for word in words:
        for match in re.finditer(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE):
            occurrences.append({
                'word': match.group(0),
                'start': match.start(),
                'end': match.end(),
                'suggested': replacement_words.get(word.lower(), word)
            })
    occurrences.sort(key=lambda x: x['start'])
    return occurrences

def replace_occurrence(text, occ):
    before = text[:occ['start']]
    after = text[occ['end']:]
    return before + occ['suggested'] + after

with col2:
    occurrences = get_word_occurrences(st.session_state.user_text, words_to_highlight)
    for idx, occ in enumerate(occurrences):
        button_label = f"Replace '{occ['word']}' with '{occ['suggested']}'"
        if st.button(button_label, key=f"{occ['word']}_{occ['start']}_{occ['end']}_{idx}"):
            st.session_state.user_text = replace_occurrence(st.session_state.user_text, occ)
            st.experimental_rerun()

# ---------- Project Save Logic ----------
PROJECTS_FILE = "projects.json"
TOKEN_FILE = "tokens.json"

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def get_tokens(username):
    tokens = load_json(TOKEN_FILE, {})
    return tokens.get(username, 50)

def update_tokens(username, change):
    tokens = load_json(TOKEN_FILE, {})
    tokens[username] = max(0, tokens.get(username, 50) + change)
    save_json(TOKEN_FILE, tokens)
    st.session_state.tokens = tokens[username]

def load_projects():
    return load_json(PROJECTS_FILE, [])

def save_projects(projects):
    save_json(PROJECTS_FILE, projects)

# ---------- Save Section ----------
st.markdown("---")
st.subheader("💾 Save Your Work as a Project")
st.session_state.tokens = get_tokens(st.session_state.username)
st.markdown(f"**Tokens Available:** {st.session_state.tokens}")

project_name = st.text_input("Project Name")
if st.button("Save Project"):
    if st.session_state.tokens >= 5:
        if not project_name.strip():
            st.error("Project name cannot be empty.")
        elif not st.session_state.user_text.strip():
            st.error("Project content is empty.")
        else:
            projects = load_projects()
            projects.append({
                "id": len(projects) + 1,
                "name": project_name.strip(),
                "content": st.session_state.user_text,
                "owner": st.session_state.username,
                "sharedWith": []
            })
            save_projects(projects)
            update_tokens(st.session_state.username, -5)
            st.success(f"Saved project '{project_name}' and deducted 5 tokens.")
    else:
        st.error("Not enough tokens to save a project.")
