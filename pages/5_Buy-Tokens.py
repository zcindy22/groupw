import streamlit as st
from supabase_proj.db_utils import add_tokens
import re
from datetime import datetime

st.set_page_config(page_title="Buy Tokens", layout="centered")
st.title("Buy Tokens")

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'x' not in st.session_state:
    st.session_state.x = None

def is_valid_card_number(number):
    clean_number = re.sub(r"\D", "", number)
    return len(clean_number) == 16 and clean_number.isdigit()

def is_valid_name(name):
    return re.fullmatch(r"[A-Za-z\s]{2,50}", name) is not None

def is_valid_expiry(expiry):
    match = re.fullmatch(r"(0[1-9]|1[0-2])\/(\d{2})", expiry)
    if not match:
        return False
    month, year = int(match.group(1)), int(match.group(2))
    now = datetime.now()
    expiry_year = 2000 + year
    expiry_date = datetime(expiry_year, month, 1)
    return expiry_date > now.replace(day=1)

def is_valid_cvv(cvv):
    return re.fullmatch(r"\d{3,4}", cvv) is not None

if st.session_state.logged_in:
    def buy_tokens():
        st.write("Select your token amount.")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button("20 tokens"):
                st.session_state.x = 20
        with col2:
            if st.button("50 tokens"):
                st.session_state.x = 50
        with col3:
            if st.button("100 tokens"):
                st.session_state.x = 100
        with col4:
            if st.button("200 tokens"):
                st.session_state.x = 200

        st.write(st.session_state.x if st.session_state.x != None else "0"," tokens to be added to ", st.session_state.email, "account!")

        with st.form("credit_card_form"):
            st.subheader("Enter Credit Card Details")

            card_number = st.text_input("Card Number", help="Enter 16-digit card number (e.g., 4242 4242 4242 4242)")
            cardholder_name = st.text_input("Cardholder Name", help="Only letters and spaces allowed")
            expiry_date = st.text_input("Expiry Date (MM/YY)")
            cvv = st.text_input("CVV", type="password", max_chars=4)

            submit = st.form_submit_button("Submit")

            if submit:
                errors = []
                if  st.session_state.x == None:
                    errors.append("Select a token amount")
                if not is_valid_card_number(card_number):
                    errors.append("Invalid card number")
                if not is_valid_name(cardholder_name):
                    errors.append("Cardholder name must only contain letters and spaces")
                if not is_valid_expiry(expiry_date):
                    errors.append("Expiry date must be valid")
                if not is_valid_cvv(cvv):
                    errors.append("CVV invalid")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    try: 
                        add_tokens(st.session_state.x)
                        st.success(f"{ st.session_state.x } tokens added successfully!")
                        st.write("Card Number:", "xxxx xxxx xxxx", card_number[-4:])
                        st.write("Cardholder Name:", cardholder_name)


                    except Exception as e: 
                        st.error(f"Error: {e}")

    if __name__ == "__main__":
        buy_tokens()

else: 
    st.write("Please log in first.")