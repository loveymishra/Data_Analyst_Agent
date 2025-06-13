import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
from pathlib import Path
import sys

# Add the parent directory to the Python path to import from core and utils
sys.path.append(str(Path(__file__).parent.parent))

from core.agent import DataAnalystAgent
from utils.parsers import parse_csv, parse_excel, parse_pdf, parse_docx, parse_image

# Page configuration
st.set_page_config(
    page_title="Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = {}
if 'agent' not in st.session_state:
    st.session_state.agent = DataAnalystAgent()

def clear_chat_history():
    """Clear the chat history"""
    st.session_state.messages = []
    st.rerun()

def process_uploaded_file(uploaded_file):
    """Process uploaded file and cache the parsed data"""
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            data = parse_csv(uploaded_file)
            st.session_state.uploaded_data[uploaded_file.name] = {
                'type': 'dataframe',
                'data': data,
                'summary': f"CSV file with {len(data)} rows and {len(data.columns)} columns"
            }
        elif file_extension in ['xlsx', 'xls']:
            data = parse_excel(uploaded_file)
            st.session_state.uploaded_data[uploaded_file.name] = {
                'type': 'dataframe',
                'data': data,
                'summary': f"Excel file with {len(data)} rows and {len(data.columns)} columns"
            }
        elif file_extension == 'pdf':
            text = parse_pdf(uploaded_file)
            st.session_state.uploaded_data[uploaded_file.name] = {
                'type': 'text',
                'data': text,
                'summary': f"PDF file with {len(text.split())} words"
            }
        elif file_extension == 'docx':
            text = parse_docx(uploaded_file)
            st.session_state.uploaded_data[uploaded_file.name] = {
                'type': 'text',
                'data': text,
                'summary': f"DOCX file with {len(text.split())} words"
            }
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            image = parse_image(uploaded_file)
            st.session_state.uploaded_data[uploaded_file.name] = {
                'type': 'image',
                'data': image,
                'summary': f"Image file ({image.format}) - {image.size[0]}x{image.size[1]} pixels"
            }
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return False
        
        return True
    except Exception as e:
        st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        return False

# Main app layout
st.title("📊 Data Analyst Agent")
st.markdown("Upload your data files and ask questions to get AI-powered insights!")

# Sidebar for file uploads
with st.sidebar:
    st.header("📁 File Upload")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to analyze",
        type=['csv', 'xlsx', 'xls', 'pdf', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
        accept_multiple_files=True,
        help="Supported formats: CSV, Excel, PDF, DOCX, and common image formats"
    )
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_data:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    if process_uploaded_file(uploaded_file):
                        st.success(f"✅ {uploaded_file.name} processed successfully!")
    
    # Display uploaded files
    if st.session_state.uploaded_data:
        st.subheader("📋 Uploaded Files")
        for filename, file_info in st.session_state.uploaded_data.items():
            with st.expander(f"📄 {filename}"):
                st.write(f"**Type:** {file_info['type'].title()}")
                st.write(f"**Summary:** {file_info['summary']}")
                
                # Show preview for dataframes
                if file_info['type'] == 'dataframe':
                    st.write("**Preview:**")
                    st.dataframe(file_info['data'].head(), use_container_width=True)
                
                # Show preview for images
                elif file_info['type'] == 'image':
                    st.image(file_info['data'], caption=filename, use_column_width=True)
    
    # Clear data button
    if st.session_state.uploaded_data:
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.uploaded_data = {}
            st.rerun()
    
    # Clear chat history button
    if st.session_state.messages:
        if st.button("🧹 Clear Chat History", type="secondary"):
            clear_chat_history()

# Main chat interface
st.header("💬 Chat with Your Data")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display any charts that were generated
        if "chart" in message:
            st.pyplot(message["chart"])

# Chat input
if prompt := st.chat_input("Ask me anything about your data..."):
    # Check if any data is uploaded
    if not st.session_state.uploaded_data:
        st.warning("Please upload some data files first!")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your data..."):
            try:
                # Get response from the agent
                response, chart = st.session_state.agent.process_query(
                    prompt, 
                    st.session_state.uploaded_data,
                    st.session_state.messages
                )
                
                # Display response
                st.markdown(response)
                
                # Display chart if generated
                if chart:
                    st.pyplot(chart)
                    # Add response with chart to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "chart": chart
                    })
                else:
                    # Add response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response
                    })
                    
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.markdown("🤖 Powered by Together.ai's Llama-4-Maverick-17B-128E-Instruct-FP8")
