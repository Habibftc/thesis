import streamlit as st
from model import get_response
from pdf_model import process_documents, get_retriever, ask_question
from image import encode_image, analyze_image
from voice import get_voice_system
from PIL import Image
from about_me import show_about_me_sidebar
from dotenv import load_dotenv
import os
import json
import time

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page Config
st.set_page_config(
    page_title="LARGE MODEL DRIVEN DIGITAL HUMAN Q&A SYSTEM",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modernized chat interface
st.markdown("""
    <style>
        .user { 
            background-color: #2563EB; 
            padding: 12px; 
            border-radius: 15px; 
            margin-bottom: 12px;
            color: white;
        }
        .bot { 
            background-color: #374151; 
            padding: 12px; 
            border-radius: 15px; 
            margin-bottom: 12px;
            color: white;
        }
        .container { 
            width: 75%; 
            margin: auto; 
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #4a6fa5 0%, #3a5a8a 100%);
            color: white;
        }
        .sidebar-title { 
            color: white !important; 
            text-align: center;
        }
        .sidebar-section { 
            padding: 15px; 
            border-radius: 10px; 
            margin-bottom: 20px; 
            background-color: rgba(255,255,255,0.1);
        }
        .error { 
            color: #ff4b4b; 
        }
        .voice-btn {
            width: 100%;
            margin-bottom: 10px;
        }
        .stButton>button {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
        }
        .stTextInput>div>div>input {
            padding: 12px;
            border-radius: 8px;
        }
        .mode-icon {
            font-size: 1.2em;
            margin-right: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "voice_system" not in st.session_state:
    st.session_state.voice_system = get_voice_system()
if "listening" not in st.session_state:
    st.session_state.listening = False

# Function to load chat history from JSON file
def load_chat_history():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as file:
            chat_history = json.load(file)
            return chat_history
    return []

# Function to save chat history to a JSON file
def save_chat_history(messages):
    with open("chat_history.json", "w") as file:
        json.dump(messages, file)

# Load chat history at the start
st.session_state.messages = load_chat_history()

# Sidebar Navigation
with st.sidebar:
    st.markdown('<h2 class="sidebar-title">🔍 LM DigiMind Q&A</h2>', unsafe_allow_html=True)

    # Mode selection
    mode = st.radio(
        "Select Mode:",
        ["💬 Text Chat", "📄 PDF Q&A", "🖼️ Image Analysis", "🎙️ Voice Chat"],
        index=0,
        key="mode_selector",
        help="Select the interaction mode"
    )

    # Settings section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")
    temperature = st.slider(
        "Response Creativity",
        0.0, 1.0, 0.7,
        help="Higher values produce more creative responses"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []  # Clear chat history
        save_chat_history(st.session_state.messages)  # Save the empty chat history to file
        st.success("Chat history cleared!")

    # Mode-specific controls
    if mode == "📄 PDF Q&A":
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📄 PDF Options")
        uploaded_files = st.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader",
            help="Upload one or more PDF documents"
        )
        if uploaded_files:
            if st.button("Process PDFs", help="Extract text and create search index"):
                with st.spinner("Processing PDFs..."):
                    try:
                        vector_store = process_documents({f.name: f for f in uploaded_files})
                        st.session_state.retriever = get_retriever()
                        st.session_state.pdf_processed = True
                        st.success("PDFs processed successfully!")
                    except Exception as e:
                        st.error(f"Failed to process PDFs: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

    elif mode == "🖼️ Image Analysis":
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Image Options")
        uploaded_image = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png"],
            key="image_uploader",
            help="Upload an image for analysis"
        )
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.session_state.uploaded_image = encode_image(uploaded_image)
            st.image(image, caption='Uploaded Image', use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif mode == "🎙️ Voice Chat":
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🎙️ Voice Settings")
        auto_play = st.checkbox(
            "Auto-play responses",
            value=True,
            help="Automatically speak AI responses"
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Main Content Area
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🤖 LM DigiMind Q&A</h1>",
            unsafe_allow_html=True)

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "bot"
        if message.get("type") == "image":
            st.image(message["content"], caption='Uploaded Image', use_column_width=True)
        else:
            st.markdown(f"<div class='{role}'>{message['content']}</div>", unsafe_allow_html=True)

# Handle different modes
if mode == "💬 Text Chat":
    user_input = st.chat_input("Type your message here...", key="chat_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            st.markdown(f"<div class='user'>{user_input}</div>", unsafe_allow_html=True)

        with st.spinner("Thinking..."):
            response = get_response(user_input)
            st.session_state.messages.append({"role": "bot", "content": response})
            with chat_container:
                st.markdown(f"<div class='bot'>{response}</div>", unsafe_allow_html=True)

        # Save chat history after every interaction
        save_chat_history(st.session_state.messages)

elif mode == "📄 PDF Q&A":
    if st.session_state.get('pdf_processed', False):
        question = st.chat_input("Ask about the PDFs...", key="pdf_question")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with chat_container:
                st.markdown(f"<div class='user'>{question}</div>", unsafe_allow_html=True)

            with st.spinner("Searching documents and generating answer..."):
                answer = ask_question(question, st.session_state.retriever)
                st.session_state.messages.append({"role": "bot", "content": answer})
                with chat_container:
                    st.markdown(f"<div class='bot'>{answer}</div>", unsafe_allow_html=True)

            # Save chat history after every interaction
            save_chat_history(st.session_state.messages)
    else:
        st.info("Please upload and process PDF files first using the sidebar options.")

elif mode == "🖼️ Image Analysis":
    if st.session_state.uploaded_image:
        question = st.chat_input("Ask about the image...", key="image_question")
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with chat_container:
                st.markdown(f"<div class='user'>{question}</div>", unsafe_allow_html=True)

            with st.spinner("Analyzing image..."):
                response = analyze_image(st.session_state.uploaded_image, question)
                st.session_state.messages.append({"role": "bot", "content": response})
                with chat_container:
                    st.markdown(f"<div class='bot'>{response}</div>", unsafe_allow_html=True)

            # Save chat history after every interaction
            save_chat_history(st.session_state.messages)
    else:
        st.info("Please upload an image first using the sidebar options.")

elif mode == "🎙️ Voice Chat":
    col1, col2 = st.columns([1, 1])
    with col1:
        voice_btn = st.button(
            "🎤 Press & Speak",
            key="voice_input_btn",
            help="Press and hold to speak",
            type="primary"
        )

    with col2:
        play_btn = st.button(
            "🔊 Play Last Response",
            key="play_response_btn",
            disabled=not st.session_state.messages or st.session_state.messages[-1]["role"] != "bot"
        )

    if voice_btn:
        with st.spinner("Listening... Speak now"):
            st.session_state.listening = True
            user_input = st.session_state.voice_system.listen()
            st.session_state.listening = False

            if user_input and user_input not in ["Could not understand audio", "Error with speech recognition service"]:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with chat_container:
                    st.markdown(f"<div class='user'>{user_input}</div>", unsafe_allow_html=True)

                with st.spinner("Thinking..."):
                    response = st.session_state.voice_system.voice_chat(user_input)
                    st.session_state.messages.append({"role": "bot", "content": response})
                    with chat_container:
                        st.markdown(f"<div class='bot'>{response}</div>", unsafe_allow_html=True)

                    if auto_play:
                        st.session_state.voice_system.speak(response)
                
                # Save chat history after every interaction
                save_chat_history(st.session_state.messages)
            else:
                st.error(user_input)

    if play_btn and st.session_state.messages and st.session_state.messages[-1]["role"] == "bot":
        st.session_state.voice_system.speak(st.session_state.messages[-1]["content"])

    user_input = st.chat_input("Or type your message here...", key="voice_chat_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            st.markdown(f"<div class='user'>{user_input}</div>", unsafe_allow_html=True)

        with st.spinner("Thinking..."):
            response = st.session_state.voice_system.voice_chat(user_input)
            st.session_state.messages.append({"role": "bot", "content": response})
            with chat_container:
                st.markdown(f"<div class='bot'>{response}</div>", unsafe_allow_html=True)

            if auto_play:
                st.session_state.voice_system.speak(response)
        
        # Save chat history after every interaction
        save_chat_history(st.session_state.messages)


show_about_me_sidebar()
# Add footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        Zhengzhou University · Developed by Habib(202180090141)· © 2025
    </div>
    """,
    unsafe_allow_html=True
)

