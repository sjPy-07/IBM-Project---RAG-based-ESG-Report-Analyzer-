import os
import json
import pandas as pd
import plotly.graph_objects as go
import gradio as gr

from src.pdf_processor import PDFProcessor
from src.rag_engine import RAGEngine
from src.analyzers import ESGAnalyzer
from src.scoring import ESGScorer

# --------------------------------------------------
# Global singletons
# --------------------------------------------------
pdf_processor = PDFProcessor()
rag_engine = RAGEngine()
analyzer = ESGAnalyzer()
scorer = ESGScorer()

COMPANY_DATA = {}
PROCESSED_FILES = []

# --------------------------------------------------
# PDF Processing
# --------------------------------------------------
def process_pdfs(files):
    if not files:
        return "❌ No files uploaded"

    os.makedirs("data/esg_reports", exist_ok=True)

    for file in files:
        filename = os.path.basename(file.name)
        save_path = os.path.join("data", "esg_reports", filename)

        # Save uploaded file
        with open(file.name, "rb") as src:
            with open(save_path, "wb") as dst:
                dst.write(src.read())

        # Extract text & create chunks
        text = pdf_processor.extract_text_from_pdf(save_path)
        chunks = pdf_processor.chunk_text(text)

        # Add documents to RAG engine
        rag_engine.add_documents(
            chunks,
            [{"source": filename, "chunk": i} for i in range(len(chunks))]
        )

        # Analyze metrics & score
        metrics = analyzer.extract_metrics(text[:15000])
        score = scorer.calculate_overall_score(metrics)

        COMPANY_DATA[filename] = {"metrics": metrics, "score": score}

        if filename not in PROCESSED_FILES:
            PROCESSED_FILES.append(filename)

    return f"✅ Successfully processed {len(files)} report(s)"

# --------------------------------------------------
# Q&A
# --------------------------------------------------
def answer_question(question):
    if not PROCESSED_FILES:
        return "❗ Please upload and process reports first."

    result = rag_engine.query(question)

    if "error" in result:
        return result["error"]

    answer_text = f"### 📝 Answer\n{result['answer']}\n\n### 📚 Sources\n"
    for doc in result["source_documents"]:
        answer_text += f"- **{doc.metadata.get('source')}**\n"

    return answer_text

# --------------------------------------------------
# Greenwashing Detection
# --------------------------------------------------
def detect_greenwashing(statement):
    if not statement.strip():
        return "❗ Please enter a sustainability statement."

    result = analyzer.detect_greenwashing(statement)

    if "error" in result:
        return result["error"]

    # Extract scores from nested criteria_scores
    criteria = result.get("criteria_scores", {})
    specificity = criteria.get("specificity", {}).get("score", "N/A")
    timeline = criteria.get("timeline", {}).get("score", "N/A")
    action_vs_intent = criteria.get("action_vs_intent", {}).get("score", "N/A")
    measurability = criteria.get("measurability", {}).get("score", "N/A")
    vagueness = criteria.get("vagueness", {}).get("score", "N/A")

    return json.dumps({
        "Greenwashing Score": f"{result.get('greenwashing_score','N/A')}/10",
        "Verdict": result.get("verdict", "N/A"),
        "Specificity": specificity,
        "Timeline": timeline,
        "Measurability": measurability,
        "Action vs Intent": action_vs_intent,
        "Vagueness": vagueness,
        "Red Flags": result.get("red_flags", []),
        "Recommendations": result.get("recommendations", [])
    }, indent=2)


# --------------------------------------------------
# Metrics Dashboard
# --------------------------------------------------
def show_metrics():
    if not PROCESSED_FILES:
        return None, None

    # Combine metrics of all processed companies into a table
    all_data = []
    radar_fig = go.Figure()
    for filename, data in COMPANY_DATA.items():
        score = data["score"]

        # Add radar for each company
        radar_fig.add_trace(go.Scatterpolar(
            r=[
                score["environmental"]["score"],
                score["social"]["score"],
                score["governance"]["score"]
            ],
            theta=["Environmental", "Social", "Governance"],
            fill="toself",
            name=filename
        ))

        all_data.append({
            "Company": filename,
            "Environmental": score["environmental"]["score"],
            "Social": score["social"]["score"],
            "Governance": score["governance"]["score"],
            "Overall": score["overall_score"],
            "Rating": score["rating"]
        })

    radar_fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 10])),
        showlegend=True
    )

    table = pd.DataFrame(all_data)

    return radar_fig, table

# --------------------------------------------------
# UI
# --------------------------------------------------
with gr.Blocks(title="🌍 ESG Report Analyzer") as app:
    gr.Markdown("# 🌍 ESG Report Analyzer")

    # File upload & process
    with gr.Row():
        file_input = gr.File(file_types=[".pdf"], file_count="multiple")
        process_btn = gr.Button("Process Reports")

    status = gr.Markdown()

    # PDF processing button
    process_btn.click(
        fn=process_pdfs,
        inputs=file_input,
        outputs=status
    )

    # Tabs
    with gr.Tabs():
        # TAB 1: Q&A
        with gr.Tab("❓ Q&A"):
            question_input = gr.Textbox(label="Ask a question")
            answer_output = gr.Markdown()
            gr.Button("Get Answer").click(
                fn=answer_question,
                inputs=question_input,
                outputs=answer_output
            )

        # TAB 2: Greenwashing Detection
        with gr.Tab("⚠️ Greenwashing Detection"):
            statement_input = gr.Textbox(lines=6, label="Sustainability Statement")
            result_output = gr.Code(language="json")
            gr.Button("Analyze").click(
                fn=detect_greenwashing,
                inputs=statement_input,
                outputs=result_output
            )

        # TAB 3: Metrics Dashboard
        with gr.Tab("📊 Metrics Dashboard"):
            radar_plot = gr.Plot()
            metrics_table = gr.Dataframe()
            gr.Button("Show Metrics").click(
                fn=show_metrics,
                inputs=[],
                outputs=[radar_plot, metrics_table]
            )

app.launch(theme=gr.themes.Soft())