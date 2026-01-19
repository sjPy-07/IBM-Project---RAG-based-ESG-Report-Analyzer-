import os
from dotenv import load_dotenv

# 1. Corrected Modern Imports (2026 Standards)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Use the classic package for these specific helper functions
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

class RAGEngine:
    """
    RAG System for ESG report analysis 
    """
    
    def __init__(self, persist_directory: str = "data/chromadb"):
        # Embeddings 
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.persist_directory = persist_directory
        self.vectorstore = None 
        
        # Initialize Groq 
        self.llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature=0.15
        )
        
    def add_documents(self, texts: list, metadatas: list = None):
        print(f"Adding {len(texts)} documents to vector database ...")
        
        if self.vectorstore is None:
            # Create new vectorstore (Persists automatically in langchain-chroma)
            self.vectorstore = Chroma.from_texts(
                texts=texts, 
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory=self.persist_directory
            )
        else:
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas
            )
        print("Documents added successfully!")
            
    def load_existing_database(self):
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("Loading existing database")
            return True 
        return False 
    
    def query(self, question: str, k: int = 4) -> dict:
        """
        Query the RAG system using the modern LCEL chain pattern.
        """
        if self.vectorstore is None:
            return {"error": "No documents loaded. Please add documents first."}
        
        # 1. Define the System Prompt
        system_prompt = (
            "You are an expert ESG report analyst. Use the following pieces of context from ESG reports to answer "
            "the question at the end. If you don't know the answer based on the context, say 'I cannot find the "
            "information in the provided reports.' Don't make up information. Always cite which company or report "
            "information comes from.\n\n"
            "Context: {context}"
        )
        
        # 2. Create the Chat Prompt Template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        
        # 3. Create the 'Combine Documents' chain (the generation part)
        combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # 4. Create the Retrieval Chain (combines retriever + generator)
        # Fix: 'retreiver' typo from original code corrected to 'retriever'
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
        
        # 5. Invoke the chain
        result = rag_chain.invoke({"input": question})
        
        # Return format consistent with your original code
        return {
            "answer": result["answer"],
            "source_documents": result["context"]
        }
        
    def similarity_search(self, query: str, k: int = 4) -> list:
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)

    
# Test the RAG engine 

if __name__ == "__main__":
    from pdf_processor import PDFProcessor
    
    # Initialize 
    processor = PDFProcessor()
    rag = RAGEngine()
    
    # Process a pdf 
    print("Processing PDF ...")
    text = processor.extract_text_from_pdf(".\data\esg_reports\\truecaller_2023.pdf")
    chunks = processor.chunk_text(text, chunk_size=1000, overlap=200)
    
    # Add to rag system 
    metadatas = [{"source" : "truecaller_2023.pdf", "chunk" : i} for i in range(len(chunks))]
    rag.add_documents(chunks, metadatas)
    
    # Test queries 
    print("\n" + "="*50)
    print("Testing RAG System")
    print("="*50 + "\n")
    
    # questions 
    questions_set1 = [
        "What initiatives has Truecaller taken to reduce its carbon footprint and energy consumption?",
        "How does Truecaller address user data privacy and security as part of its social responsibility?",
        "What governance practices does Truecaller follow to ensure ethical business conduct and regulatory compliance?"
    ]
    
    questions_set2 = [
        "Does Truecaller mention using renewable energy in its operations?",
        "Is user privacy explicitly listed as a social responsibility in Truecaller's ESG report?",
        "Does Truecaller have a formal code of ethics or governance policy?"
    ]
    
    # testing for question set 1 
    print("\n\nTesting for question set - 1")
    
    for i, q in enumerate(questions_set1, 1):
        print(f"Q - {i} : {q}")
        
        result = rag.query(q, k=3)
        print(f"Ans : {result['answer']}\n")
        print("\t\t\t\t-" * 30, "\n")
        
    # testing for question set 2
    print("=" * 40, end="\n\n")
    print("\n\nTesting for question set - 2")
    
    for i, q in enumerate(questions_set1, 1):
        print(f"Q - {i} : {q}")
        
        result = rag.query(q, k=3)
        print(f"Ans : {result['answer']}\n")
        print("\t\t\t\t-" * 30, "\n")