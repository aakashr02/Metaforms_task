# Document AI Processor

### Key Features

1. Complete File Support:
  <br> PDFs (text extraction via PyPDF2)
  <br> Word documents (via python-docx)
  <br> Plain text files
  <br> Direct text input

2. Two Processing Modes:
  <br> Automatic Extraction: AI determines the optimal JSON structure
  <br> Schema-Guided: Provide your own JSON template for structured output

3. Full OpenAI Integration:
  <br> Proper API key handling
  <br> Model selection (GPT-4 or GPT-3.5)
  <br> Adjustable parameters (temperature, max tokens)

4. User-Friendly Output:
  <br> Formatted JSON display
  <br> Downloadable results

### How to Run
Install requirements:

  <br> pip install streamlit openai PyPDF2 python-docx pandas
  <br> Save as document_ai_app.py

Run with:
  <br> streamlit run document_ai.py



### Flow Diagram

<img width="1808" height="1798" alt="deepseek_mermaid_20250715_ad95cd" src="https://github.com/user-attachments/assets/9d9b86ef-625a-40d6-8eac-baf9ac91e232" />


