from langchain_groq import ChatGroq
from PyPDF2 import PdfReader
from docx import Document
import os

llm = ChatGroq(
    temperature=0, 
    groq_api_key='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', 
    model_name="llama-3.1-70b-versatile"
)

def process_cvs(upload_folder, job_description, result_folder):
    results = []

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

        # Prepare the prompt for LLM
        prompt = f"""
        Analyze the following CV:
        {text}

        Job Description:
        {job_description}

        Provide a ranking score and explanation.
        """
        response = llm.invoke(prompt).content
        results.append((file, response))

    # Save results in a text file
    os.makedirs(result_folder, exist_ok=True)
    result_file = os.path.join(result_folder, 'analysis_results.txt')

    with open(result_file, 'w') as f:
        for file, response in results:
            f.write(f"CV: {file}\nResponse:\n{response}\n\n")

    return 'analysis_results.txt'
