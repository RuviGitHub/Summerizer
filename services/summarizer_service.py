import pdfplumber
import requests
import logging

class SummarizerService:
    def __init__(self):
        from transformers import pipeline
        logging.info("Loading the Hugging Face summarization model...")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        logging.info("Model loaded successfully.")

    def fetch_and_summarize(self, file_url):
        try:
            logging.info(f"Fetching document from URL: {file_url}")
            response = requests.get(file_url)
            response.raise_for_status()

            logging.info("Document fetched successfully.")

            # Save the PDF temporarily to extract text
            temp_pdf_path = "temp_document.pdf"
            with open(temp_pdf_path, "wb") as temp_file:
                temp_file.write(response.content)

            # Extract text from PDF
            text = self.extract_text_from_pdf(temp_pdf_path)
            logging.info("Text extracted from PDF.")

            # Split and summarize
            chunks = self.split_into_chunks(text, max_chunk_size=1024)
            summary_points = []
            for index, chunk in enumerate(chunks):
                logging.info(f"Summarizing chunk {index + 1}/{len(chunks)}...")
                summary = self.summarizer(chunk, max_length=150, min_length=50, do_sample=False)
                summary_text = summary[0]['summary_text']
                summary_points.append(f"- {summary_text}")
                logging.info(f"Chunk {index + 1} summarized successfully.")

            logging.info("All chunks summarized successfully.")
            return "\n".join(summary_points)

        except Exception as e:
            logging.error(f"Error summarizing document: {e}")
            return "Error summarizing document."

    def extract_text_from_pdf(self, pdf_path):
        """Extracts and returns text content from a PDF file."""
        text_content = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text_content += page.extract_text() or ""
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
        return text_content

    def split_into_chunks(self, text, max_chunk_size):
        words = text.split()
        chunks = []
        chunk = []

        for word in words:
            chunk.append(word)
            if len(" ".join(chunk)) > max_chunk_size:
                chunks.append(" ".join(chunk))
                chunk = []

        if chunk:
            chunks.append(" ".join(chunk))

        return chunks


