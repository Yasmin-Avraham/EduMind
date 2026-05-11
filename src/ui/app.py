import streamlit as st
import requests

st.set_page_config(page_title="EduMind AI", layout="wide")

if "token" not in st.session_state:
    st.title("🔐 EduMind Portal")

    #choose role before login
    role_choice = st.radio("Who are you?", ["Parent", "Teacher"], horizontal=True)

    with st.form("login_form"):
        if role_choice == "Parent":
            user_id = st.text_input("Enter Student ID (Teudat Zehut)")
            payload = {"student_id": int(user_id) if user_id.isdigit() else None}
        else:
            user_id = st.text_input("Enter Class ID (e.g., T1)")
            payload = {"class_id": user_id}

        submit = st.form_submit_button("Login")

        if submit:
            if not user_id:
                st.error("Please enter a valid ID")
            else:
                try:
                    #
                    res = requests.post("http://localhost:8000/login", json=payload)
                    if res.status_code == 200:
                        # take the token from the Header
                        st.session_state.token = res.headers.get("Authorization")
                        st.session_state.user_role = role_choice.lower()
                        st.success(f"Welcome, {role_choice}!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Server error: {e}")

# after login
else:
    st.sidebar.title("📊 Quick Info")

    st.title("🤖 EduMind - AI Advisor")

    # chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask me about the student or regulations..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # call to /chat
        headers = {"Authorization": st.session_state.token}
        response = requests.post("http://localhost:8000/chat",
                                 json={"query": prompt},
                                 headers=headers)

        if response.status_code == 200:
            answer = response.json()["response"]
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})