# supabase_proj/ui_utils.py
import streamlit as st

def header(text: str):
    """Big consistent page header."""
    st.markdown(f"## {text}")

def primary_button(label: str) -> bool:
    """Styled primary button—returns True when clicked."""
    return st.button(label)

def token_bar(balance: int):
    """Displays the user’s token balance in a consistent spot."""
    st.markdown(f"**Token Balance:** {balance}")
