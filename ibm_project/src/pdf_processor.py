# modules 

import fitz
import os 
from typing import List, Dict

# PDF processor class 

class PDFProcessor:
    """
        Extracts and processes text from PDF files.
    """
    
    def __init__(self):
        self.supported_formats = ['pdf']
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """_summary_
        Extracts all text from a pdf file.
        
        Args:
            pdf_path (str): Path to pdf file 

        Returns:
            str: Extracted text as string 
        """
        
        try:
            # Open the pdf 
            doc = fitz.open(pdf_path)
            text = ""
            page_cnt = len(doc)
            
            # Extract text from each page 
            for pg_no, page in enumerate(doc, 1):
                text += f"\n---- Page {pg_no} ----\n"
                text += page.get_text()
                
            doc.close()
            return text 
        
        except Exception as e:
            print(f"Error processing {pdf_path} : {str(e)}")
            return ""
        
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """_summary_
        Split text into overlapping chunks.
        
        Args:
            text (str): Text to chunk 
            chunk_size (int, optional): Size of each chunk in characters 
            overlap (int, optional): Overlap between chunks 

        Returns:
            List[str]: List of chunks 
        """
        
        chunks = []
        start = 0 
        
        while start < len(text):
            finish = start + chunk_size 
            chunk = text[start:finish]
            
            # Try to break at sentence boundary 
            if finish < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:
                    chunk = chunk[:break_point + 1]
                    finish = start + break_point + 1
                    
            chunks.append(chunk.strip())
            start = finish - overlap
            
        return chunks 
    
    
    def extract_metadata(self, pdf_path: str) ->  Dict:
        """_summary_
        Extract metadata from pdf file 
        
        Args:
            pdf_path (str): Path to pdf file 

        Returns:
            Dict: Dictionary containing details such as author, title, page count, and more.
        """
        
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                'filename' : os.path.basename(pdf_path),
                'page_count' : len(doc),
                'title': doc.metadata.get('title', 'Unknown'),
                'author': doc.metadata.get('author', 'Unknown')
            }
            
            doc.close()
            return metadata
        except:
            return {'filename':os.path.basename(pdf_path), 'error': True}
        
# Test the processor 
if __name__ == "__main__":
    processor = PDFProcessor()
    
    # Testing with a sample pdf 
    # sample_pdf = ".\data\esg_reports\Bajaj Finserv Ltd - ESG Report.pdf"
    sample_pdf = ".\data\esg_reports\\truecaller_2023.pdf"
    print("got the file location! Started workinng ...\n")
    
    # Text extraction 
    print("\nExtracting text ...")
    text = processor.extract_text_from_pdf(sample_pdf)
    print(f"\tExtracted {len(text)} characters")
    print("\tDisplaying the first 200 characters:\n", text[:200])
    
    # Chunking
    print("\nChunking the text ...")
    chunks = processor.chunk_text(text)
    print(f"\tCreated {len(chunks)} chunks")
    print(f"\tFirst chunk :\n", chunks[0][:200]) 
    
    # Extracting the metadata 
    print("\nExtracting the metadata ...")
    metadata = processor.extract_metadata(sample_pdf)
    print(metadata)