import streamlit as st

def save_user_to_url(username, user_id):
    st.query_params.update({"username": username, "user_id": user_id})
                                     
def load_user_from_url():
    params = st.query_params
    username = params.get("username")
    user_id = params.get("user_id")
    return username, user_id  
