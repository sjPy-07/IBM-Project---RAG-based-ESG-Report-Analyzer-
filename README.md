# IBM-Project---RAG-based-ESG-Report-Analyzer-
## IBM Project - RAG based ESG Report Analyzer 

RAG based ESG (Environment, Social, and Governance) Report Analyzer application, that can be used to ask questions to get context specific answers from the pdf (specified with source, page numbers), flag greenwashing, provide a sustainability score to the report.

The RAG based chat feature allows you to get context specific details from the massive pdfs in very less time. 

Tech Stack Used : 
- Frontend: Gradio (final version), streamlit (testing)
- AI/NLP: Google Gemini API (free tier), Groq API, LangChain
- RAG System: ChromaDB (vector database), HuggingFace Embeddings
- PDF Processing: PyMuPDF
- Visualization: Plotly, Pandas
- Python Version : 3.11


## File Org
ibm_project(esg-analyzer)/
|-gradio_app1.py
|-gradio_app2.py
|.env
|-src/
|  |-analyzers.py
|  |-pdf_processor.py
|  |-rag_engine.py
|  |-scoring.py
|-prompts/
|  |-sample_commits.txt
|  |-sample_gwd.txt
|  |-sample_metric.txt
|-data/
|  |-esg_reports
|  |-chromadb
|--- README.md

### Credits 
Flow chart image generated using Nano Banana Pro 


