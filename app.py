from app import create_app
import os

if __name__ == '__main__':
    app = create_app()

    # Create necessary directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    app.run(debug=True)
