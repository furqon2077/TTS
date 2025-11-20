import streamlit as st
from pathlib import Path
from openai import OpenAI
import tempfile
import docx
import pdfplumber

st.title("TTS Generator with OpenAI GPT-4o Mini TTS")

def extract_text(file):
    """Extract text from TXT, DOCX, PDF."""
    if file.type == "text/plain":
        return file.read().decode("utf-8")

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file.type == "application/pdf":
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    else:
        return ""


api_key = st.text_input("OpenAI API Key", type="password")

uploaded_file = st.file_uploader(
    "Upload TXT, DOCX, or PDF file (optional)",
    type=["txt", "docx", "pdf"]
)

text_input = st.text_area("Or enter text manually:")

language = st.selectbox(
    "Select language",
    ["English", "Russian", "Uzbek", "Turkish", "Spanish", "German", "French"],
    index=0
)

voice = st.selectbox("Voice", ["coral", "verse", "alloy"], index=0)

if st.button("Generate MP3"):
    if not api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    # Extract text from file OR text area
    final_text = ""

    if uploaded_file:
        final_text = extract_text(uploaded_file)

    if not final_text.strip():
        final_text = text_input

    if not final_text.strip():
        st.error("Please provide text either by uploading a file or typing manually.")
        st.stop()

    try:
        client = OpenAI(api_key=api_key)
        tmp_path = Path(tempfile.gettempdir()) / "speech.mp3"


        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=final_text,
            instructions=
            f"Speak in {language}.Use natural pronunciation and clarity.\n\n{final_text}"
        ) as response:
            response.stream_to_file(tmp_path)

        audio_data = tmp_path.read_bytes()

        st.audio(audio_data, format="audio/mp3")

        st.download_button(
            "Download MP3",
            data=audio_data,
            file_name="speech.mp3",
            mime="audio/mpeg"
        )
        st.success("MP3 generated successfully!")

    except Exception as e:
        st.error(f"Error: {e}")