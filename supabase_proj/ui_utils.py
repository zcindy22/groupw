# supabase_proj/ui_utils.py

import streamlit as st

def header(text: str):
    st.markdown(f"## {text}")

def primary_button(label: str, key: str = None) -> bool:
    return st.button(label, key=key)

def token_bar(balance: int):
    st.markdown(f"**Token Balance: `{balance}`**")
