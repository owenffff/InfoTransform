"""
Audio processor for handling speech-to-text using OpenAI Whisper API
"""

import os
from openai import OpenAI
from config import config


class AudioProcessor:
    def __init__(self):
        """Initialize the audio processor with OpenAI-compatible client"""
        self.client = OpenAI(
            api_key=config.API_KEY,
            base_url=config.BASE_URL
        )
    
    def process_file(self, file_path):
        """
        Process an audio file and transcribe it to text
        
        Args:
            file_path (str): Path to the audio file to process
            
        Returns:
            dict: Processing result with transcribed text and metadata
        """
        try:
            # Open and read the audio file
            with open(file_path, 'rb') as audio_file:
                # Use Whisper API for transcription
                transcript = self.client.audio.transcriptions.create(
                    model=config.WHISPER_MODEL,
                    file=audio_file,
                    response_format="text"
                )
            
            # Format the transcript as Markdown
            markdown_content = self._format_transcript_as_markdown(
                transcript,
                os.path.basename(file_path)
            )
            
            return {
                'success': True,
                'content': markdown_content,
                'filename': os.path.basename(file_path),
                'type': 'audio'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filename': os.path.basename(file_path),
                'type': 'audio'
            }
    
    def _format_transcript_as_markdown(self, transcript, filename):
        """
        Format the transcript as a Markdown document
        
        Args:
            transcript (str): The transcribed text
            filename (str): Original audio filename
            
        Returns:
            str: Formatted Markdown content
        """
        markdown = f"""# Audio Transcription

**Source File:** {filename}  
**Transcription Date:** {self._get_current_timestamp()}

---

## Transcript

{transcript}

---

*Transcribed using OpenAI Whisper API*
"""
        return markdown
    
    def _get_current_timestamp(self):
        """Get current timestamp in a readable format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def is_supported_file(self, filename):
        """Check if the file type is supported for audio processing"""
        ext = filename.lower().split('.')[-1]
        return ext in config.ALLOWED_AUDIO_EXTENSIONS
