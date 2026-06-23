import json
import os

import requests
import streamlit as st


BACKEND_URL = "http://127.0.0.1:8000"
CHAT_HISTORY_FILE = "chat_history.json"


st.set_page_config(
    page_title="Anuj AI Lab",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Anuj AI Lab")


# ---------- Functions ----------

def load_chat_history():

    if os.path.exists(CHAT_HISTORY_FILE):

        with open(
            CHAT_HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    return []


def save_chat_history():

    with open(
        CHAT_HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            st.session_state.messages,
            file,
            indent=4
        )


# ---------- Load history ----------

if "messages" not in st.session_state:

    st.session_state.messages = load_chat_history()


# ---------- Sidebar ----------

st.sidebar.title("⚙ Controls")

if st.sidebar.button("Clear Chat"):

    st.session_state.messages = []

    save_chat_history()

# Backend status

try:

    requests.get(
        f"{BACKEND_URL}/"
    )

    backend_status = "🟢 Online"

except:

    backend_status = "🔴 Offline"

st.sidebar.subheader("System")

st.sidebar.write(
    f"Backend: {backend_status}"
)

st.sidebar.write(
    "Version: 1.0.0"
)

st.sidebar.write(
    "Phase: 2"
)

st.sidebar.write(
    "Day: 6"
)

st.sidebar.divider()

st.sidebar.subheader(
    "About"
)

st.sidebar.write(
    "Anuj AI Lab"
)

st.sidebar.write(
    "Local Multi-Agent AI Platform"
)

st.sidebar.divider()

st.sidebar.write(
    f"Conversations: {len(st.session_state.messages)//2}"
)

st.sidebar.divider()

# Export chat

chat_json = json.dumps(
    st.session_state.messages,
    indent=4
)

st.sidebar.download_button(
    label="📥 Download JSON",
    data=chat_json,
    file_name="chat_history.json",
    mime="application/json"
)


# ---------- Display history ----------

for message in st.session_state.messages:

    avatar = "👤"

    if message["role"] == "assistant":

        avatar = "🤖"

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        if isinstance(
            message["content"],
            dict
        ):

            st.json(
                message["content"]
            )

        else:

            st.write(
                message["content"]
            )


# ---------- User input ----------

prompt = st.chat_input(
    "Ask anything..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.write(
            prompt
        )

    try:

        response = requests.get(
            f"{BACKEND_URL}/route",
            params={
                "query": prompt
            }
        )

        result = response.json()

    except Exception as e:

        result = {
            "error": str(e)
        }

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result
        }
    )

    save_chat_history()

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        st.json(
            result
        )