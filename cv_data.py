import os
import re
import requests
from PyPDF2 import PdfReader
from docx import Document

# ✅ Groq API Key
API_KEY = "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"
API_URL = "https://api.groq.com/v1/inference"
MODEL_NAME = "llama-3.1-70b-versatile"

# ✅ Function to extract text from PDF files
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()

# ✅ Function to extract text from DOCX files
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text.strip()

# ✅ Function to interact with the Groq API for CV refinement and data extraction
def refine_and_extract_data_with_llm(cv_text):
    prompt = (
        "Extract the following details from the provided CV text: \n"
        "- Name \n"
        "- Phone Number \n"
        "- Email Address \n"
        "- LinkedIn Profile Link \n"
        "- Skills \n"
        "- Work Experience \n"
        "- Education \n"
        "- Certifications \n"
        "Provide the information in JSON format. \n"
        f"CV Text: {cv_text}"
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 2048,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            result = response.json()
            return result.get("text", {}).strip()
        except Exception as e:
            print(f"Error processing API response: {e}")
            return None
    else:
        print(f"API request failed with status code {response.status_code}: {response.text}")
        return None

# ✅ Function to save structured data to a TXT file
def save_to_txt(file_name, structured_data):
    output_dir = "extracted_data"
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(output_dir, file_name.replace(" ", "_").replace(".pdf", ".txt").replace(".docx", ".txt"))

    with open(output_file_path, "w") as file:
        file.write(structured_data)

    print(f"Data saved to {output_file_path}")

# ✅ Function to process files in a given directory
def process_directory(directory_path):
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if not os.path.isfile(file_path):
            continue

        print(f"Processing {file_name}...")
        if file_name.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_name.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            print(f"Unsupported file format: {file_name}")
            continue

        if text:
            structured_data = refine_and_extract_data_with_llm(text)
            if structured_data:
                save_to_txt(file_name, structured_data)
            else:
                print(f"Failed to process data for {file_name}")
        else:
            print(f"No text found in {file_name}")

# ✅ Main function
if __name__ == "__main__":
    directory = input("Enter the path of the directory containing CVs (PDF or DOCX): ")
    if os.path.isdir(directory):
        process_directory(directory)
    else:
        print("Invalid directory path.")
