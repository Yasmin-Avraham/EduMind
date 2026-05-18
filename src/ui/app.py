import streamlit as st
import requests

st.set_page_config(page_title="EduMind AI", layout="wide", page_icon="🎓")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "token" not in st.session_state:
    st.title("🔐 EduMind Portal")
    role_choice = st.radio("Who are you?", ["Parent", "Teacher"], horizontal=True)

    with st.form("login_form"):
        user_id_input = st.text_input("Enter ID")
        submit = st.form_submit_button("Login")

        if submit:
            if not user_id_input:
                st.error("Please enter an ID")
            else:
                role = role_choice.lower()
                payload = {"student_id": int(user_id_input)} if role == "parent" and user_id_input.isdigit() else {
                    "class_id": user_id_input}

                try:
                    res = requests.post("http://localhost:8000/login", json=payload)
                    if res.status_code == 200:
                        st.session_state.token = res.headers.get("Authorization") or res.json().get("access_token")
                        st.session_state.role = role
                        st.session_state.user_identifier = user_id_input
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid ID or Connection Error")
                except Exception as e:
                    st.error(f"Server error: {e}")

else:
    with st.sidebar:
        st.title("📊 Profile")
        st.info(f"Connected as: **{st.session_state.role}**\n\nID: {st.session_state.user_identifier}")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    st.title("🤖 EduMind - AI Advisor")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Please ask me a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        chat_payload = {"query": prompt}
        if st.session_state.role == "parent":
            chat_payload["student_id"] = int(st.session_state.user_identifier)
        else:
            chat_payload["class_id"] = st.session_state.user_identifier

        headers = {"Authorization": st.session_state.token}

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                with requests.post(
                        "http://localhost:8000/chat",
                        json=chat_payload,
                        headers=headers,
                        stream=True,
                        timeout=None
                ) as r:
                    if r.status_code == 200:
                        for chunk in r.iter_content(chunk_size=1024):
                            if chunk:
                                chunk_str = chunk.decode("utf-8", errors="ignore")
                                full_response += chunk_str
                                response_placeholder.markdown(full_response + "▌")

                        response_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    else:
                        st.error(f"Error: {r.status_code}")
            except Exception as e:
                st.error(f"Connection error: {e}")