"""
Flask application for Markitdown MVP
"""

import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from config import Config
from processors import VisionProcessor, AudioProcessor
import tempfile
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Initialize processors
vision_processor = None
audio_processor = None

def init_processors():
    """Initialize processors with error handling"""
    global vision_processor, audio_processor
    try:
        Config.validate()
        vision_processor = VisionProcessor()
        audio_processor = AudioProcessor()
        return True
    except Exception as e:
        print(f"Error initializing processors: {e}")
        return False

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Save the file temporarily
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    try:
        # Determine which processor to use
        if vision_processor and vision_processor.is_supported_file(filename):
            result = vision_processor.process_file(file_path)
        elif audio_processor and audio_processor.is_supported_file(filename):
            result = audio_processor.process_file(file_path)
        else:
            result = {
                'success': False,
                'error': f'Unsupported file type: {filename}'
            }
        
        # Clean up the uploaded file
        os.remove(file_path)
        
        return jsonify(result)
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_markdown():
    """Generate and download markdown file"""
    data = request.get_json()
    content = data.get('content', '')
    filename = data.get('filename', 'output.md')
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    # Generate download filename
    base_name = os.path.splitext(filename)[0]
    download_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    return send_file(
        tmp_path,
        as_attachment=True,
        download_name=download_name,
        mimetype='text/markdown'
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'processors_initialized': vision_processor is not None and audio_processor is not None
    })

if __name__ == '__main__':
    # Initialize processors
    if init_processors():
        print("✅ Processors initialized successfully")
        print(f"🚀 Starting server on http://localhost:{Config.FLASK_PORT}")
        app.run(debug=True, port=Config.FLASK_PORT)
    else:
        print("❌ Failed to initialize processors. Please check your configuration.")
