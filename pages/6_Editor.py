# streamlit/pages/5_Editor.py
import streamlit as st
from supabase_proj.ui_utils     import header, primary_button, token_bar
from supabase_proj.db_utils     import (
    charge_for_action,
    get_token_balance,
    submit_blacklist_word
)

from supabase_proj.llm_service  import correct

st.set_page_config(page_title="Paid Editor", layout="wide")

def count_word_changes(orig: str, edited: str) -> int:
    o, e = orig.split(), edited.split()
    return sum(1 for x, y in zip(o, e) if x != y) + abs(len(o) - len(e))

def self_correction_flow(text: str, user_id: str):
    edited = st.text_area("Edit in place:", value=text, key="self_edit")
    if primary_button("Submit Self-Edits"):
        changes = count_word_changes(text, edited)
        try:
            new_bal = charge_for_action(user_id, "self_edit", words_changed=changes)
            token_bar(new_bal)
            st.success(f"{changes} words changed → charged {changes//2} tokens")
        except ValueError as err:
            st.error(str(err))

def llm_assist_flow(text: str, user_id: str):
    if not primary_button("Run LLM-Assist"):
        return
    suggestions = correct(text)
    if not suggestions:
        st.info("No suggestions.")
        return

    for s in suggestions:
        span = text[s["start"]:s["end"]]
        st.markdown(f"- `{span}` → **{s['suggestion']}**")
        c1, c2 = st.columns(2)
        if c1.button(f"Accept {s['id']}"):
            _charge_and_notify(user_id, "llm_accept", "Accepted suggestion")
        if c2.button(f"Reject {s['id']}"):
            _charge_and_notify(user_id, "llm_reject", "Rejected suggestion")


def _charge_and_notify(user_id: str, action: str, msg: str):
    try:
        new_bal = charge_for_action(user_id, action)
        token_bar(new_bal)
        st.success(msg)
    except ValueError as err:
        st.error(str(err))

def main():
    header("Paid User Editor")
    st.write("Welcome to the Paid User's Editor Page")
    # auth guard is temporarily disabled to focus on LLM & blacklist
    # require_paid_user()

    # use a dummy or real user_id
    user_id = st.session_state.get("user_id", "8969e3f6-05ee-40e8-9868-4aefd8ccfb73")

    # show current balance (fallback to 100 if no real user)
    try:
        balance = get_token_balance(user_id)
    except Exception:
        balance = 100
    token_bar(balance)

    # main draft input
    original = st.text_area("Enter your text:", height=250, key="orig_text")

    # now three tabs instead of two
    tab1, tab2, tab3 = st.tabs([
        "Self-Correction",
        "LLM-Assist",
        "Suggest A Blacklist Word"
    ])

    with tab1:
        self_correction_flow(original, user_id)

    #with tab2:
        llm_assist_flow(original, user_id)

    with tab3:
        st.subheader("Submit a word to the blacklist:")
        candidate = st.text_input("Word to blacklist:", key="blk_word")
        if primary_button("Submit Word"):
            if not candidate.strip():
                st.warning("Please enter a non-empty word.")
            else:
                try:
                    submit_blacklist_word(user_id, candidate.strip())
                    st.success(f"‘{candidate}’ submitted for super-user review.")
                except Exception as err:
                    st.error(f"Failed to submit: {err}")

if __name__ == "__main__":
    main()