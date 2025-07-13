import streamlit as st
import time
import re
import os
import requests

# رابط API التحليل (FastAPI على Render)
os.environ["BACKEND_URL"] = "https://translation-api-lo00.onrender.com"
BACKEND_URL = os.getenv("BACKEND_URL")

# دالة الاتصال مع API وتحليل الترجمة
@st.cache_data(show_spinner=False)
def analyze_translation(english, arabic):
    if not BACKEND_URL:
        return "❌ BACKEND_URL not set."
    try:
        resp = requests.post(
            f"{BACKEND_URL.rstrip('/')}/analyze",
            json={"english": english, "arabic": arabic},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        reasoning = data.get("reasoning", "❌ لا يوجد تحليل.")
        precise = data.get("precise_translation", "—")
        return f"**📝 سبب الخطأ:** {reasoning}\n\n**✅ الترجمة الدقيقة المقترحة:**\n{precise}"
    except Exception as e:
        return f"❌ Error contacting backend: {e}"

# كشف اللغة
def detect_language(text):
    english_pattern = re.compile(r'^[A-Za-z0-9\s.,?!\'\";:-]+$')
    arabic_pattern = re.compile(r'^[\u0600-\u06FF\s0-9.,؟!،؛:]+$')
    if english_pattern.fullmatch(text.strip()):
        return "en"
    elif arabic_pattern.fullmatch(text.strip()):
        return "ar"
    return None

# واجهة Streamlit
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
    add_message("assistant", "👋 Hello! I’m your translation assistant.")
    add_message("assistant", "Please type the English sentence you'd like to translate.")

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# صندوق إدخال المستخدم
prompt = st.chat_input("Type your message here...")

if prompt:
    add_message("user", prompt)

    if st.session_state.step == 1:
        if detect_language(prompt) != "en":
            add_message("assistant", "⚠️ Please enter the sentence in **English** using only English letters.")
        else:
            st.session_state.english_sentence = prompt
            with st.chat_message("assistant"):
                with st.spinner("Assistant is typing..."):
                    time.sleep(1)
                    reply = "Great! Now, please provide the Arabic translation."
                    st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.step = 2

    elif st.session_state.step == 2:
        if detect_language(prompt) != "ar":
            add_message("assistant", "⚠️ Please enter the translation in **Arabic** using only Arabic letters.")
        else:
            st.session_state.arabic_translation = prompt
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your translation..."):
                    analysis = analyze_translation(
                        st.session_state.english_sentence,
                        st.session_state.arabic_translation
                    )
                    st.markdown(analysis)
            st.session_state.messages.append({"role": "assistant", "content": analysis})
            add_message("assistant", "Would you like to try another sentence? Type it in English to continue.")
            st.session_state.step = 1

