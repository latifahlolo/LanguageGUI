import streamlit as st
import time
import re
import os
import requests

# ✅ ngrok رابط الـ backend الجديد (الموديل شغال عليه)
os.environ["BACKEND_URL"] = "https://f4b152d28832.ngrok-free.app"
BACKEND_URL = os.getenv("BACKEND_URL")

@st.cache_data(show_spinner=False)
def analyze_translation(english, arabic):
    if not BACKEND_URL:
        return "❌ BACKEND_URL not set."
    try:
        resp = requests.post(
            f"{BACKEND_URL.rstrip('/')}/analyze",
            json={"english": english, "arabic": arabic},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("analysis", "❌ لا يوجد تحليل.")
    except Exception as e:
        return f"❌ Error contacting backend: {e}"

def detect_language(text):
    english_pattern = re.compile(r'^[A-Za-z0-9\s.,?!\'\";:-]+$')
    arabic_pattern = re.compile(r'^[\u0600-\u06FF\s0-9.,؟!،؛:]+$')
    if english_pattern.fullmatch(text.strip()):
        return "en"
    elif arabic_pattern.fullmatch(text.strip()):
        return "ar"
    return None

# ========== واجهة المستخدم ========== #
st.set_page_config(page_title="Translation Analyzer", layout="centered")
st.title("💬 Translation Chatbot")

if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.english_sentence = ""
    st.session_state.arabic_translation = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    with st.chat_message(role):
        st.markdown(content)

if not st.session_state.messages:
    add_message("assistant", "👋 Welcome! I’ll help you analyze English ↔ Arabic translations.")
    add_message("assistant", "Please enter a sentence in **English** to begin.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message here...")

if prompt:
    add_message("user", prompt)

    if st.session_state.step == 1:
        if detect_language(prompt) != "en":
            add_message("assistant", "⚠️ Please enter the sentence in **English**.")
        else:
            st.session_state.english_sentence = prompt
            reply = "✅ Got it! Now, enter your Arabic translation of the sentence."
            add_message("assistant", reply)
            st.session_state.step = 2

    elif st.session_state.step == 2:
        if detect_language(prompt) != "ar":
            add_message("assistant", "⚠️ Please enter the translation in **Arabic**.")
        else:
            st.session_state.arabic_translation = prompt
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your translation..."):
                    result = analyze_translation(
                        st.session_state.english_sentence,
                        st.session_state.arabic_translation
                    )
                    st.markdown(result)
            add_message("assistant", "Would you like to try another sentence? Type it in English to start over.")
            st.session_state.step = 1
