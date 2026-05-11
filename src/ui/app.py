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

                if role == "parent":
                    if user_id_input.isdigit():
                        payload = {"student_id": int(user_id_input)}
                    else:
                        st.error("Student ID must be a number (numeric only)")
                        st.stop()
                else:
                    payload = {"class_id": user_id_input}
            try:
                res = requests.post("http://localhost:8000/login", json=payload)
                if res.status_code == 200:
                    st.session_state.token = res.headers.get("Authorization") or res.json().get("access_token")
                    st.session_state.role = role
                    st.session_state.user_identifier = user_id_input
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid ID")
            except Exception as e:
                st.error(f"Server is down? {e}")

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

    if prompt := st.chat_input("How is the student doing?"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        chat_payload = {"query": prompt}
        if st.session_state.role == "parent":
            chat_payload["student_id"] = int(st.session_state.user_identifier)
        else:
            chat_payload["class_id"] = st.session_state.user_identifier

        headers = {"Authorization": st.session_state.token}

        with st.spinner("Talking to AI..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json=chat_payload,
                    headers=headers,
                    timeout=None
                )

                if response.status_code == 200:
                    answer = response.json().get("response", "No response from AI")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    with st.chat_message("assistant"):
                        st.markdown(answer)
                else:
                    st.error(f"Server Error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to FastAPI: {e}")
