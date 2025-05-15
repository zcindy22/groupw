# pages/7_Editor.py

import streamlit as st
from supabase_proj.ui_utils import header, primary_button, token_bar
from supabase_proj.db_utils import (
    charge_for_action, get_token_balance, get_blacklist, submit_blacklist_word, words_to_tokens, chars_to_tokens, apply_token_penalty
)
from supabase_proj.llm_service import correct, feedback

st.set_page_config(page_title="Test Editor", layout="wide")


def count_word_changes(orig: str, edited: str) -> int:
    o, e = orig.split(), edited.split()
    return sum(1 for x, y in zip(o, e) if x != y) + abs(len(o) - len(e))


def self_correction_flow(text: str, user_id: str):
    edited = st.text_area("Edit the text manually:", value=text, key="self_edit")
    if primary_button("Submit Self-Correction", key="btn_self"):
        changes = count_word_changes(text, edited)
        cost = changes // 2
        try:
            charge_for_action(user_id, "self_edit", words_changed=changes)
            st.session_state.tokens_used += cost
            st.session_state.corrections_self += changes
            st.success(f"{changes} words changed → Charged {cost} tokens.")
        except Exception as e:
            st.error(f"Token charge failed: {e}")


def llm_assist_flow(text: str, user_id: str):
    if not primary_button("Run LLM Correction", key="btn_llm"):
        return

    suggestions = correct(text)
    if not suggestions:
        st.info("No corrections suggested.")
        if len(text.split()) > 10:
            charge_for_action(user_id, "error_free_bonus")
            st.session_state.tokens_used -= 3  # Net change
            st.success(" No issues found — bonus +3 tokens!")
        return

    for s in suggestions:
        span = text[s["start"]:s["end"]]
        st.markdown(f"- `{span}` → **{s['suggestion']}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            if primary_button(f"Accept {s['id']}", key=f"acc_{s['id']}"):
                charge_for_action(user_id, "llm_accept")
                feedback(user_id, s["id"], "accept")
                st.session_state.tokens_used += 1
                st.session_state.corrections_llm += 1
        with c2:
            reason_key = f"reason_{s['id']}"
            st.text_input("Reason to reject:", key=reason_key)
            if primary_button(f"Reject {s['id']}", key=f"rej_{s['id']}"):
                reason = st.session_state.get(reason_key, "").strip()
                if reason:
                    charge_for_action(user_id, "llm_reject")
                    feedback(user_id, s["id"], "reject", reason=reason)
                    st.warning("Submitted rejection for review.")
                    st.session_state.tokens_used += 5
                else:
                    st.error("Reason required.")
        with c3:
            if primary_button(f"Mark Correct {s['id']}", key=f"ign_{s['id']}"):
                feedback(user_id, s["id"], "mark_correct")
                st.info("Marked as correct — will not be flagged again.")


def main():
    # st.warning("Loaded Paid Editor successfully")  #testing to see if page loads
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to access the Paid Editor.")
        return

    user_id = st.session_state.get("user_id", "guest-id")

    # Session stats
    for key in ["tokens_used", "corrections_self", "corrections_llm", "total_submissions"]:
        if key not in st.session_state:
            st.session_state[key] = 0

    # Token balance
    try:
        bal = get_token_balance(user_id)
    except Exception:
        bal = 0

    header("Paid Editor Page")
    token_bar(bal)

    with st.expander("Session Stats", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Balance", f"{bal}")
        c2.metric("Used", f"{st.session_state.tokens_used}")
        c3.metric("Self", f"{st.session_state.corrections_self}")
        c4.metric("LLM", f"{st.session_state.corrections_llm}")
        c5.metric("Submissions", f"{st.session_state.total_submissions}")

    # Input
    raw_text = st.text_area("Enter your text:", height=250)

    if not raw_text.strip():
        return

    word_count = len(raw_text.split())
    required_tokens = words_to_tokens(word_count)

    if required_tokens > bal:
        apply_token_penalty(user_id)
        st.error(f"Not enough tokens: need {required_tokens}, have {bal}. Penalty applied.")
        return

    # Charge for text submission
    charge_for_action(user_id, "submit_text", amount=-required_tokens)
    st.session_state.tokens_used += required_tokens
    st.session_state.total_submissions += 1

    # Blacklist filtering
    blacklist = get_blacklist()
    filtered_words = []
    blacklist_chars = 0

    for word in raw_text.split():
        if word.lower() in blacklist:
            filtered_words.append('*' * len(word))
            blacklist_chars += len(word)
        else:
            filtered_words.append(word)

    if blacklist_chars > 0:
        token_cost = chars_to_tokens(blacklist_chars)
        charge_for_action(user_id, "blacklist", amount=-token_cost)
        st.session_state.tokens_used += token_cost

    filtered_text = " ".join(filtered_words)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Self Correction",
        "LLM Correction",
        "Suggest Blacklist Word",
        "Save to File"
    ])

    with tab1:
        self_correction_flow(filtered_text, user_id)

    with tab2:
        llm_assist_flow(filtered_text, user_id)

    with tab3:
        st.subheader("Suggest a new blacklist word:")
        word = st.text_input("Blacklist Word", key="blk_word")
        if primary_button("Submit Word", key="btn_blk"):
            if not word.strip():
                st.warning("Please enter a word.")
            else:
                try:
                    submit_blacklist_word(user_id, word.strip())
                    st.success(f"‘{word}’ has been submitted and is pending review by a Super User.")
                except Exception as err:
                    st.error(f"Submission failed: {err}")

    with tab4:
        filename = st.text_input("Filename", "edited_output.txt")
        if primary_button("Save to File", key="btn_save"):
            if bal < 5:
                st.error("Not enough tokens to save (5 required).")
            else:
                with open(filename, "w") as f:
                    f.write(st.session_state.get("self_edit", filtered_text))
                charge_for_action(user_id, "save_file")
                st.session_state.tokens_used += 5
                st.success(f"Saved to {filename}. 5 tokens deducted.")


#if __name__ == '__main__':
main()