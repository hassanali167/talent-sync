# import os
# from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app
# from werkzeug.utils import secure_filename
# from PyPDF2 import PdfReader

# main = Blueprint('main', __name__)

# ALLOWED_EXTENSIONS = {'pdf'}

# def allowed_file(filename):
#     """Check if the file has an allowed extension."""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @main.route('/')
# def index():
#     """Render the HTML page."""
#     return render_template('index.html')

# @main.route('/upload', methods=['POST'])
# def upload_files():
#     """Handle file uploads and convert them to a TXT file."""
#     if 'files' not in request.files:
#         return jsonify({'error': 'No files part in the request'}), 400

#     files = request.files.getlist('files')
#     if not files:
#         return jsonify({'error': 'No files provided'}), 400

#     uploaded_files = []
#     for file in files:
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#             file.save(upload_path)
#             uploaded_files.append(upload_path)

#     # Combine and convert PDFs to a single TXT file
#     combined_text = ""
#     for filepath in uploaded_files:
#         combined_text += extract_text_from_pdf(filepath) + "\n\n"

#     output_filename = "combined_cv_data.txt"
#     output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
#     with open(output_path, 'w') as txt_file:
#         txt_file.write(combined_text)

#     return jsonify({'txt_file': output_filename})

# @main.route('/download/<filename>', methods=['GET'])
# def download_file(filename):
#     """Provide a route to download the generated TXT file."""
#     directory = current_app.config['OUTPUT_FOLDER']
#     return send_from_directory(directory, filename, as_attachment=True)

# def extract_text_from_pdf(filepath):
#     """Extract text from a PDF file."""
#     try:
#         reader = PdfReader(filepath)
#         text = ""
#         for page in reader.pages:
#             text += page.extract_text() or ""
#         return text
#     except Exception as e:
#         return f"Error reading {filepath}: {str(e)}"






import os
from flask import Blueprint, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfReader
import re

main = Blueprint('main', __name__)  # Convert to Blueprint

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Helper: Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file_path):
    text = ""
    try:
        reader = PdfReader(pdf_file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file_path):
    text = ""
    try:
        doc = Document(docx_file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

# Function to extract specific sections from the text
def extract_sections(text):
    sections = {
        "Name": "",
        "Email": "",
        "Skills": "",
        "Experience": "",
        "About": "",
        "LinkedIn": ""
    }

    # Extract "Name" (Assumes the first line is the name)
    lines = text.splitlines()
    if lines:
        sections["Name"] = lines[0].strip()

    # Extract "Email"
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        sections["Email"] = email_match.group(0)

    # Extract "LinkedIn Profile"
    linkedin_match = re.search(r"(https?://www\.linkedin\.com/[^\s]+)", text)
    if linkedin_match:
        sections["LinkedIn"] = linkedin_match.group(0)

    # Extract "Skills"
    skills_match = re.search(r"(?i)(skills)[:\-]?\s*(.*?)(experience|education|$)", text, re.DOTALL)
    if skills_match:
        sections["Skills"] = skills_match.group(2).strip()

    # Extract "Experience"
    experience_match = re.search(r"(?i)(experience|work history)[:\-]?\s*(.*?)(education|skills|$)", text, re.DOTALL)
    if experience_match:
        sections["Experience"] = experience_match.group(2).strip()

    # Extract "About"
    about_match = re.search(r"(?i)(about|summary|profile|introduction|biography)[:\-]?\s*(.*?)(experience|skills|education|$)", text, re.DOTALL)
    if about_match:
        sections["About"] = about_match.group(2).strip()

    return sections

# Function to process a single file
def process_file(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    # Extract text
    if file_path.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        extracted_text = extract_text_from_docx(file_path)
    else:
        return None

    # Extract specific sections
    extracted_sections = extract_sections(extracted_text)

    # Save refined content to a .txt file
    txt_file_path = os.path.join(PROCESSED_FOLDER, f"{file_name}.txt")
    with open(txt_file_path, "w") as txt_file:
        for key, value in extracted_sections.items():
            txt_file.write(f"{key}: {value}\n")

    return txt_file_path

# Route: Render the HTML page
@main.route('/')
def index():
    return render_template('index.html')

# Route: Handle file upload
@main.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({"error": "No files uploaded"}), 400

    saved_txt_files = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # Process the file
            processed_file = process_file(save_path)
            if processed_file:
                saved_txt_files.append(os.path.basename(processed_file))

    if not saved_txt_files:
        return jsonify({"error": "No valid files processed"}), 400

    return jsonify({"txt_files": saved_txt_files}), 200

# Route: Download processed file
@main.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404
