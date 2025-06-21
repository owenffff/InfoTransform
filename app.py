"""
Flask application for Markitdown MVP
"""

import os
import asyncio
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from config import config
from processors import VisionProcessor, AudioProcessor, BatchProcessor
import tempfile
from datetime import datetime
import zipfile

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.TEMP_EXTRACT_DIR, exist_ok=True)

# Initialize processors
vision_processor = None
audio_processor = None
batch_processor = None

def init_processors():
    """Initialize processors with error handling"""
    global vision_processor, audio_processor, batch_processor
    try:
        config.validate()
        vision_processor = VisionProcessor()
        audio_processor = AudioProcessor()
        batch_processor = BatchProcessor(vision_processor, audio_processor)
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
    file_path = os.path.join(config.UPLOAD_FOLDER, filename)
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

@app.route('/upload-batch', methods=['POST'])
def upload_batch():
    """Handle multiple file uploads and batch processing"""
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'success': False, 'error': 'No files selected'}), 400
    
    # Save uploaded files temporarily
    saved_files = []
    files_info = []
    
    try:
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                saved_files.append(file_path)
                
                # Check if it's a ZIP file
                if batch_processor.is_zip_file(filename):
                    # Check ZIP file size
                    if os.path.getsize(file_path) > config.MAX_ZIP_SIZE:
                        raise Exception(f"ZIP file {filename} exceeds maximum size of {config.MAX_ZIP_SIZE // (1024*1024)}MB")
                    
                    # Extract ZIP and get file info
                    extracted_files = batch_processor.extract_zip_with_structure(file_path)
                    files_info.extend(extracted_files)
                else:
                    # Regular file
                    files_info.append({
                        'path': filename,
                        'full_path': file_path,
                        'filename': filename
                    })
        
        # Process files asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                batch_processor.process_multiple_files(files_info)
            )
        finally:
            loop.close()
        
        # Clean up uploaded files
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Clean up extracted files
        batch_processor.cleanup_temp_dirs()
        
        return jsonify(result)
        
    except Exception as e:
        # Clean up on error
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        batch_processor.cleanup_temp_dirs()
        
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download-batch', methods=['POST'])
def download_batch():
    """Download batch processing results as combined markdown or ZIP"""
    data = request.get_json()
    results = data.get('results', [])
    format_type = data.get('format', 'markdown')  # 'markdown' or 'zip'
    
    if not results:
        return jsonify({'success': False, 'error': 'No results to download'}), 400
    
    try:
        if format_type == 'zip':
            # Create ZIP archive with individual markdown files
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                zip_path = batch_processor.create_zip_archive(results, tmp_file.name)
            
            download_name = f"markitdown_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/zip'
            )
        else:
            # Create combined markdown file
            combined_content = batch_processor.create_combined_markdown(results)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
                tmp_file.write(combined_content)
                tmp_path = tmp_file.name
            
            download_name = f"markitdown_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            return send_file(
                tmp_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='text/markdown'
            )
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        print(f"🚀 Starting server on http://localhost:{config.FLASK_PORT}")
        app.run(debug=True, port=config.FLASK_PORT)
    else:
        print("❌ Failed to initialize processors. Please check your configuration.")
