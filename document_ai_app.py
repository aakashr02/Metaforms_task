import streamlit as st
import openai
import json
import PyPDF2
from docx import Document
from io import BytesIO


# Configure app
st.set_page_config(page_title="Document AI Processor", layout="wide")
st.title("📄 Document AI Processor")
st.markdown("""
Extract structured data from documents using AI.  
Supports **PDFs, Word docs, and text files**.
""")

# ===== File Processing Functions =====
def extract_text(file):
    """Extract text from uploaded file"""
    if file.type == "application/pdf":
        try:
            reader = PyPDF2.PdfReader(BytesIO(file.getvalue()))
            return "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            st.error(f"PDF error: {str(e)}")
            return None
    
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(BytesIO(file.getvalue()))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Word error: {str(e)}")
            return None
    
    elif file.type == "text/plain":
        return str(file.getvalue(), "utf-8")
    
    else:
        st.error(f"Unsupported file type: {file.type}")
        return None

# ===== Sidebar Configuration =====
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Configuration
    api_key = st.text_input("OpenAI API Key", type="password", 
                          help="Get your key from platform.openai.com")
    
    model = st.selectbox(
        "AI Model",
        ["gpt-4-turbo-preview", "gpt-3.5-turbo"],
        index=0,
        help="GPT-4 for better accuracy, GPT-3.5 for faster results"
    )
    
    # Extraction Options
    extraction_mode = st.radio(
        "Extraction Type",
        ["Automatic (AI determines structure)", 
         "Schema-Guided (Provide JSON template)"],
        index=0
    )
    
    # Advanced Options
    with st.expander("Advanced Settings"):
        temperature = st.slider("Creativity", 0.0, 1.0, 0.3)
        max_tokens = st.number_input("Max Tokens", 256, 4000, 1500)

# ===== Main Interface =====
uploaded_file = st.file_uploader(
    "Upload document (PDF, DOCX, TXT)", 
    type=["pdf", "docx", "txt"],
    accept_multiple_files=False
)

text_input = st.text_area("Or paste text directly", height=150)

# Schema input (conditionally shown)
schema = None
if extraction_mode == "Schema-Guided (Provide JSON template)":
    schema = st.text_area(
        "JSON Schema Template", 
        height=150,
        placeholder='''{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "date": {"type": "string", "format": "date"}
  }
}'''
    )

# ===== Processing Section =====
if st.button("🚀 Process Document", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your OpenAI API key")
        st.stop()
    
    # Get input text
    input_text = ""
    if uploaded_file:
        input_text = extract_text(uploaded_file)
        if not input_text:
            st.stop()
    elif text_input:
        input_text = text_input
    else:
        st.error("Please upload a file or paste text")
        st.stop()
    
    with st.spinner("Analyzing document..."):
        try:
            # Prepare the prompt
            if extraction_mode == "Schema-Guided (Provide JSON template)":
                prompt = f"""
                Convert this document into JSON following exactly this schema:
                {schema}
                
                Document content:
                {input_text}
                
                Rules:
                1. Include all available data
                2. Mark missing fields as null
                3. Add "_confidence" scores (0-1) for each field
                4. Return ONLY valid JSON
                """
            else:
                prompt = f"""
                Analyze this document and extract structured data as comprehensive JSON.
                Include:
                - Key entities (people, organizations, locations)
                - Important dates and numbers
                - Relationships between entities
                - Key-value pairs
                - Document structure
                
                Add confidence scores for each extracted field.
                Return ONLY the JSON output.
                
                Document:
                {input_text}
                """
            
            # Call OpenAI API
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Process response
            result = response.choices[0].message.content
            
            try:
                json_data = json.loads(result)
                
                # Display results
                st.success("✅ Extraction complete!")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("Structured Data")
                    st.json(json_data)
                
                with col2:
                    st.subheader("Analysis")
                    
                    # Basic stats
                    if isinstance(json_data, dict):
                        st.metric("Total Fields", len(json_data))
                    
                    # Confidence analysis
                    if any("confidence" in str(k).lower() for k in json_data.keys()):
                        confidences = []
                        def find_confidences(data):
                            if isinstance(data, dict):
                                for k, v in data.items():
                                    if "confidence" in str(k).lower():
                                        confidences.append(v)
                                    else:
                                        find_confidences(v)
                            elif isinstance(data, list):
                                for item in data:
                                    find_confidences(item)
                        
                        find_confidences(json_data)
                        
                        if confidences:
                            avg_conf = sum(confidences)/len(confidences)
                            st.metric("Average Confidence", f"{avg_conf:.0%}")
                            st.progress(avg_conf)
                
                # Download button
                st.download_button(
                    "💾 Download JSON",
                    json.dumps(json_data, indent=2),
                    "extracted_data.json",
                    type="primary"
                )
            
            except json.JSONDecodeError:
                st.error("The AI returned invalid JSON. Below is the raw Response")
                # with st.expander("Show Raw Response"):
                st.code(result)
        
        except Exception as e:
            st.error(f"Processing failed: {str(e)}")

# ===== Instructions =====
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Upload a document** (PDF, Word, or text file) or paste text
    2. Choose extraction mode:
       - **Automatic**: AI determines the best structure
       - **Schema-Guided**: Provide your own JSON template
    3. Click "Process Document"
    4. View and download the structured results
    """)
    

# ===== Requirements =====
with st.expander("🔧 Installation"):
    st.code("""
    pip install streamlit openai PyPDF2 python-docx
    """, language="bash")