from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from services.s3_service import S3Service
from services.summarizer_service import SummarizerService
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize services
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize custom services
s3_service = S3Service()
summarizer_service = SummarizerService()


# Upload document API
@app.route("/upload", methods=["POST"])
def upload_document():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        print(f"Received file: {file.filename}")  # Log the received file name

        # Upload file to S3
        file_url = s3_service.upload_file(file, file.filename)

        if not file_url:
            return jsonify({"error": "Failed to upload file"}), 500

        print(f"File uploaded successfully: {file_url}")  # Log success
        return jsonify({"message": "File uploaded successfully", "file_url": file_url})

    except Exception as e:
        print(f"Error in upload route: {e}")  # Log errors
        return jsonify({"error": "Internal server error"}), 500


# Summarize document API
@app.route("/summarize", methods=["POST"])
def summarize_document():
    data = request.json
    file_url = data.get("file_url")

    if not file_url:
        return jsonify({"error": "No file URL provided"}), 400

    summary = summarizer_service.fetch_and_summarize(file_url)
    return jsonify({"summary": summary})


@app.route("/summarize-dynamic", methods=["POST"])
def summarize_document_dynamic():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        # Get the file from the request
        file = request.files["file"]
        logging.info(f"Received file: {file.filename}")

        # Validate file type (optional)
        if not file.filename.endswith(".pdf"):
            return (
                jsonify({"error": "Invalid file type. Only PDF files are allowed."}),
                400,
            )

        # Process the file using the summarizer service
        summary = summarizer_service.summarize_dynamic(file)

        return jsonify({"summary": summary}), 200

    except Exception as e:
        logging.error(f"Error processing summary: {e}")
        return jsonify({"error": "An internal error occurred."}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
