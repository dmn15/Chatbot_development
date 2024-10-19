#----------------------------------------
import streamlit as st
from streamlit import session_state
import time
import base64
import os
import pandas as pd
from vectors import EmbeddingsManager
from chatbot import ChatbotManager
import json 

# Function to display PDF
def displayPDF(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to display Markdown
def displayMarkdown(file):
    content = file.read().decode()
    st.markdown(content)

# Function to display CSV
def displayCSV(file):
    df = pd.read_csv(file)
    st.dataframe(df)

# Function to display JSON
def displayJSON(file):
    content = json.load(file)
    st.json(content)

# Function to display Excel
def displayExcel(file):
    df = pd.read_excel(file)
    st.dataframe(df)

# Initialize session_state variables
if 'temp_file_path' not in st.session_state:
    st.session_state['temp_file_path'] = None
if 'chatbot_manager' not in st.session_state:
    st.session_state['chatbot_manager'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'llm_choice' not in st.session_state:
    st.session_state['llm_choice'] = 'ollama'

# Function to get OpenAI API key
def get_openai_api_key():
    api_key = st.secrets.get("OPENAI_API_KEY")
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    return api_key

def initialize_chatbot_manager():
    openai_api_key = get_openai_api_key()
    
    if st.session_state['chatbot_manager'] is None or st.session_state['llm_choice'] != st.session_state['chatbot_manager'].llm_choice:
        st.session_state['chatbot_manager'] = ChatbotManager(
            model_name="BAAI/bge-m3",
            device="cpu",
            encode_kwargs={"normalize_embeddings": True},
            llm_choice=st.session_state['llm_choice'],
            llm_model="llama3.2:3b",
            llm_temperature=0.7,
            openai_api_key=openai_api_key,
            openai_model="gpt-3.5-turbo",
            openai_temperature=0.7,
            qdrant_url="http://localhost:6333",
            collection_name="Rishabh_Collection"
        )
    elif st.session_state['llm_choice'] == 'openai' and openai_api_key:
        st.session_state['chatbot_manager'].update_llm('openai', api_key=openai_api_key)

# Set the page configuration
st.set_page_config(
    page_title="Document Buddy App",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Document Assistant and Rishabh Chatbot")
    st.markdown("---")
    
    # LLM Selection
    llm_choice = st.selectbox(
        "Select Language Model",
        ["ollama", "openai"],
        key="llm_selector"
    )
    if llm_choice != st.session_state['llm_choice']:
        st.session_state['llm_choice'] = llm_choice
        st.session_state['messages'] = []  # Clear chat history when switching models
        initialize_chatbot_manager()
    
    # Check for OpenAI API key when OpenAI is selected
    if llm_choice == 'openai' and get_openai_api_key() is None:
        st.warning("OpenAI API key not found. Please set it up as described in the app instructions.")
    
    # Navigation Menu
    menu = ["🏠 Home", "🤖 Chatbot"]
    choice = st.selectbox("Navigate", menu)

# Home Page
if choice == "🏠 Home":
    st.title("📄 RAG Application")
    st.markdown("""
    Welcome to **Document Q/A and Rishabh Chatbot**!

    **Built using Open Source Stack (Llama 3.2:3b, GPT-3.5 Turbo, BGE Embeddings, and Qdrant running locally within a Docker Container.)**

    - **Upload Documents**: Easily upload your PDF, Markdown, PowerPoint, JSON, CSV, or Excel files.
    - **Chat**: Interact with your documents through our intelligent chatbot.
    """)

# Chatbot Page
elif choice == "🤖 Chatbot":
    st.title("Chatbot with " + st.session_state['llm_choice'].capitalize())
    st.markdown("---")
    
    # Create three columns
    col1, col2, col3 = st.columns(3)

    # Column 1: File Uploader and Preview
    with col1:
        st.header("📂 Upload Document (Optional)")
        uploaded_file = st.file_uploader("Upload a file", type=["pdf", "md", "ppt", "pptx", "csv", "xls", "xlsx","json"])
        if uploaded_file is not None:
            st.success("📄 File Uploaded Successfully!")
            st.markdown(f"**Filename:** {uploaded_file.name}")
            st.markdown(f"**File Size:** {uploaded_file.size} bytes")
            
            st.markdown("### 📖 File Preview")
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension == '.pdf':
                displayPDF(uploaded_file)
            elif file_extension == '.md':
                displayMarkdown(uploaded_file)
            elif file_extension in ['.csv']:
                displayCSV(uploaded_file)
            elif file_extension in ['.xls', '.xlsx']:
                displayExcel(uploaded_file)
            elif file_extension == '.json':
                displayJSON(uploaded_file)
            elif file_extension in ['.ppt', '.pptx']:
                st.warning("Preview not available for PowerPoint files.")
            
            temp_file_path = f"temp{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state['temp_file_path'] = temp_file_path

    # Column 2: Create Embeddings
    with col2:
        st.header("🧠 Embeddings")
        create_embeddings = st.checkbox("✅ Create Embeddings")
        if create_embeddings:
            if st.session_state['temp_file_path'] is None:
                st.warning("⚠️ No file uploaded. Using existing vector database.")
            else:
                try:
                    embeddings_manager = EmbeddingsManager(
                        model_name="BAAI/bge-m3",
                        device="cpu",
                        encode_kwargs={"normalize_embeddings": True},
                        qdrant_url="http://localhost:6333",
                        collection_name="Rishabh_Collection"
                    )
                    
                    with st.spinner("🔄 Embeddings are in process..."):
                        result = embeddings_manager.create_embeddings(st.session_state['temp_file_path'])
                        time.sleep(1)
                    st.success(result)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")

            initialize_chatbot_manager()

    # Column 3: Chatbot Interface
    with col3:
        st.header("💬 ChatBot")
        
        initialize_chatbot_manager()

        for msg in st.session_state['messages']:
            st.chat_message(msg['role']).markdown(msg['content'])

        user_input = st.chat_input("Type your message here...")
        if user_input:
            st.chat_message("user").markdown(user_input)
            st.session_state['messages'].append({"role": "user", "content": user_input})

            try:
                st.session_state['chatbot_manager'].initialize_llm()  # Reset callback handler
                
                # Create a placeholder for the assistant's response
                assistant_response = st.empty()
                
                # Get the streamed response
                answer = st.session_state['chatbot_manager'].get_response(user_input)
                
                # Add the response to the session state
                st.session_state['messages'].append({"role": "assistant", "content": answer})
                
                # Force a rerun to update the chat history
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ An error occurred while processing your request: {e}")

# Footer
st.markdown("---")