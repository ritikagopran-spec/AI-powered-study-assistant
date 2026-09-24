import streamlit as st
from google import genai
import os

st.set_page_config(page_title="AI Study Assistant PRO", page_icon="🧠")

# --- API KEY LOGIC: Secret me hai to wahi lega, nahi to input lega ---
# Streamlit Cloud ke liye st.secrets, local ke liye sidebar
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    key_source = "secret"
except:
    api_key = os.getenv("GEMINI_API_KEY")
    key_source = "env"
    if not api_key:
        with st.sidebar:
            api_key = st.text_input("🔑 Gemini API Key", type="password")
        key_source = "input"

if not api_key:
    st.warning("👈 Sidebar me API Key dalo ya Secrets me add karo")
    st.stop()

client = genai.Client(api_key=api_key)

# --- UI ---
with st.sidebar:
    st.title("PRO Controls")
    if key_source == "secret":
        st.success("✅ PRO Mode - Key Loaded (No need to enter)")
    st.selectbox("📚 Subject", ["Science", "Maths", "History", "Computer"], key="sub")
    st.selectbox("🎯 Mode", ["Notes Maker", "Doubt Solver", "Quiz Generator", "Explain Like I'm 5"], key="mode")
    st.selectbox("Language", ["Hinglish", "Hindi", "English"], key="lang")
    if st.button("🗑️ Chat Clear"):
        st.session_state.messages = []
        st.rerun()

st.title("🧠 AI Study Assistant PRO - New 2026")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("Sawal likho..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        prompt = f"Subject:{st.session_state.sub} Mode:{st.session_state.mode} Lang:{st.session_state.lang} Q:{q}"
        interaction = client.interactions.create(model="gemini-3.6-flash", input=prompt)
        # naya API me output_text se answer aata hai
        ans = getattr(interaction, 'output_text', str(interaction))
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})