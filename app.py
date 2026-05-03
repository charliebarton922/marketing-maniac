import streamlit as st
from marketing_maniac_logic import initialize_messages, chat_with_scout

st.set_page_config(page_title="Marketing Maniac", page_icon="📣")

st.image("images/logo.png", width=300)
st.title("Marketing Maniac")
st.write("Your AI assistant for creating marketing content.")

if st.button("Reset Chat"):
    st.session_state.messages = initialize_messages()
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = initialize_messages()

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

user_input = st.chat_input("Ask Marketing Maniac for marketing ideas...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    assistant_reply, updated_messages = chat_with_scout(
        user_input,
        st.session_state.messages
    )

    st.session_state.messages = updated_messages

    with st.chat_message("assistant"):
        st.write(assistant_reply)