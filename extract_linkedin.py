import re
import os
import csv
from docx import Document
from PyPDF2 import PdfReader

def extract_linkedin_ids(upload_folder, output_csv):
    linkedin_ids = []

    for file in os.listdir(upload_folder):
        file_path = os.path.join(upload_folder, file)
        text = ''

        if file.endswith('.pdf'):
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text()

        elif file.endswith('.docx'):
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text

        # Extract LinkedIn IDs using regex
        matches = re.findall(r'https?://(?:www\.)?linkedin\.com/in/\S+', text)
        linkedin_ids.extend([(file, match) for match in matches])

    # Save results in CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['CV Name', 'LinkedIn ID'])
        writer.writerows(linkedin_ids)
