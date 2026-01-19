import gradio as gr
import os
import shutil

from src.pdf_processor import PDFProcessor
from src.rag_engine import RAGEngine

# -------------------------------------------------
# Setup
# -------------------------------------------------
os.makedirs("data/esg_reports", exist_ok=True)

pdf_processor = PDFProcessor()
rag_engine = RAGEngine()

# -------------------------------------------------
# Core Functions
# -------------------------------------------------

def process_pdfs(files, processed_files):
    if not files:
        return processed_files, "⚠️ No files uploaded."

    status = "🔄 Processing PDFs...\n"

    for file in files:
        filename = os.path.basename(file.name)
        dest_path = os.path.join("data/esg_reports", filename)

        # Gradio files already exist on disk
        shutil.copy(file.name, dest_path)

        text = pdf_processor.extract_text_from_pdf(dest_path)
        chunks = pdf_processor.chunk_text(text)

        metadatas = [
            {"source": filename, "chunk": i}
            for i in range(len(chunks))
        ]

        rag_engine.add_documents(chunks, metadatas)
        processed_files.append(filename)

        status += f"✅ {filename} processed\n"

    return processed_files, status


def answer_question(question, processed_files):
    if not processed_files:
        return "⚠️ Please upload and process PDFs first.", "No sources available."

    if not question.strip():
        return "⚠️ Please enter a valid question.", "No sources available."

    result = rag_engine.query(question, k=4)

    # Format sources nicely
    sources_md = ""
    for i, doc in enumerate(result["source_documents"]):
        sources_md += f"""
**Source {i+1}: {doc.metadata.get('source', 'Unknown')}**

{doc.page_content[:500]}...

---
"""

    return result["answer"], sources_md


# -------------------------------------------------
# Gradio UI
# -------------------------------------------------

with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="green",
        secondary_hue="blue",
        neutral_hue="slate",
        font=["Inter", "sans-serif"]
    ),
    css="""
        .title { font-size: 34px; font-weight: 700; }
        .subtitle { font-size: 16px; color: #4b5563; margin-bottom: 20px; }
    """
) as demo:

    gr.Markdown(
        "<div class='title'>🌍 ESG Report Analyzer</div>"
        "<div class='subtitle'>Upload ESG reports and ask intelligent questions using RAG</div>"
    )

    processed_files_state = gr.State([])

    with gr.Row():
        # ---------------- LEFT PANEL ----------------
        with gr.Column(scale=1):
            gr.Markdown("### 📄 Upload ESG Reports")

            file_upload = gr.File(
                label="Upload PDF files",
                file_types=[".pdf"],
                file_count="multiple"
            )

            process_btn = gr.Button("🚀 Process PDFs", variant="primary")

            status_box = gr.Textbox(
                label="Processing Status",
                lines=8,
                interactive=False
            )

            gr.Markdown("### ✅ Processed Reports")
            processed_list = gr.JSON(label="Files")

        # ---------------- RIGHT PANEL ----------------
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Ask Questions")

            gr.Markdown(
                "- What are the company's carbon emissions?\n"
                "- What renewable energy targets do they have?\n"
                "- What is their board diversity?"
            )

            question_input = gr.Textbox(
                label="Your Question",
                placeholder="Ask something about the ESG reports..."
            )

            ask_btn = gr.Button("🔍 Get Answer", variant="primary")

            answer_box = gr.Markdown(label="Answer")

            with gr.Accordion("📚 Sources", open=False):
                sources_markdown = gr.Markdown()

    # -------------------------------------------------
    # Events
    # -------------------------------------------------

    process_btn.click(
        process_pdfs,
        inputs=[file_upload, processed_files_state],
        outputs=[processed_files_state, status_box]
    ).then(
        lambda x: x,
        inputs=processed_files_state,
        outputs=processed_list
    )

    ask_btn.click(
        answer_question,
        inputs=[question_input, processed_files_state],
        outputs=[answer_box, sources_markdown]
    )

# -------------------------------------------------
# Launch
# -------------------------------------------------
demo.launch()
