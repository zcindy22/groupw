import streamlit as st
import re

st.set_page_config(layout="wide")
st.title("TextAide")

# Example login check
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # default to not logged in

# Set word limit based on login status
word_limit = 500 if st.session_state.logged_in else 50

if 'user_text' not in st.session_state:
    st.session_state.user_text = ""

current_word_count = len(re.findall(r'\b\w+\b', st.session_state.user_text))

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
    # Always get occurrences from the current text
    occurrences = get_word_occurrences(st.session_state.user_text, words_to_highlight)
    for idx, occ in enumerate(occurrences):
        # Unique key for each button
        button_label = f"Replace '{occ['word']}' at position {occ['start']} with '{occ['suggested']}'"
        if st.button(button_label, key=f"{occ['word']}_{occ['start']}_{occ['end']}_{idx}"):
            # Replace only this occurrence in the current text
            st.session_state.user_text = replace_occurrence(st.session_state.user_text, occ)
            #st.experimental_rerun()
            st.recun() 
