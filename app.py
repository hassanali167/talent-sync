from flask import Flask, request, render_template, jsonify, send_file
import os
import shutil
from extract_linkedin import extract_linkedin_ids
from process_cvs import process_cvs

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_cvs/'
app.config['RESULT_FOLDER'] = 'output_result/'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    job_description = request.form['job_description']
    files = request.files.getlist('cvs')

    # Save uploaded files
    for file in files:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    # Process CVs: extract LinkedIn IDs and generate report
    extract_linkedin_ids(app.config['UPLOAD_FOLDER'], 'linkedin_id_extract/linkedin_ids.csv')
    report_file = process_cvs(app.config['UPLOAD_FOLDER'], job_description, app.config['RESULT_FOLDER'])

    # Clean up uploaded CVs
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return jsonify({"report_file": report_file})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['RESULT_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
