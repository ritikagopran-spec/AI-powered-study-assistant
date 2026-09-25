import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="AI Study Assistant PRO MAX", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-3.8-flash')

model = load_model()

with st.sidebar:
    st.title("PRO Controls")
    subject = st.selectbox("Subject", ["Maths", "Science", "History", "Computer", "English","general"])
    mode = st.selectbox("Mode", ["Doubt Solver", "Notes Maker", "Explain Topic", "Quiz"])
    language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])

st.title("📚 AI Study Assistant - Image + Audio + Text")

# --- 1. IMAGE UPLOAD ---
img_file = st.file_uploader("📷 Image Upload (Question ka photo)", type=["jpg","png","jpeg"])
if img_file:
    img = Image.open(img_file)
    st.image(img, width=300)

# --- 2. AUDIO UPLOAD ---
audio_file = st.file_uploader("🎤 Audio Upload (Voice question)", type=["mp3","wav","m4a"])
if audio_file:
    st.audio(audio_file)

# --- 3. TEXT INPUT ---
prompt = st.chat_input("Sawal likho / bolo - e.g. Is image ko solve karo")

if prompt or (img_file and st.button("Image Solve Karo")) or (audio_file and st.button("Audio Samjho")):
    
    final_prompt = f"You are expert {subject} teacher. Language:{language}. Mode:{mode}. User question: {prompt if prompt else 'Is image/audio ko samjhao aur solve karo'}. If maths, step-by-step with LaTeX."

    with st.chat_message("assistant"):
        try:
            content_to_send = [final_prompt]
            
            if img_file:
                content_to_send.append(img)
            
            if audio_file:
                # Audio file ko Gemini ke liye prepare karo
                audio_bytes = audio_file.read()
                content_to_send.append({"mime_type": audio_file.type, "data": audio_bytes})

            full_text = ""
            placeholder = st.empty()
            
            response = model.generate_content(content_to_send, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            
        except Exception as e:
            st.error(f"Error: {e}. Try: requirements.txt me Pillow add karo aur model gemini-3.8-flash rakho.")
