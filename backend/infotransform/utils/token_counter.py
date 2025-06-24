"""
Token counter utility using tiktoken for markdown content
"""

import tiktoken
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Global token tracking for summary reporting
_token_stats = {
    'total_files': 0,
    'total_tokens': 0,
    'files_processed': []
}


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Counts the number of tokens in the given text using TikToken.

    Args:
        text (str): The input string to be tokenized.
        encoding_name (str): Name of the token encoding. Defaults to "cl100k_base".
            You can change this to "gpt2" or another supported encoding if needed.

    Returns:
        int: The number of tokens in the text.

    Raises:
        ValueError: If text is not a string or encoding is unknown.
    """
    if not isinstance(text, str):
        raise ValueError("Input 'text' must be a string.")

    try:
        encoding = tiktoken.get_encoding(encoding_name)
    except Exception as e:
        raise ValueError(f"Unknown or unsupported encoding: {encoding_name}") from e

    tokens = encoding.encode(text)
    return len(tokens)


def log_token_count(filename: str, text: str, context: str = None) -> int:
    """
    Count and log tokens for a file with reduced verbosity
    
    Args:
        filename: Name of the file being processed
        text: The text content to count tokens for
        context: Optional context for the token counting (e.g., 'initial', 'analysis')
        
    Returns:
        int: The number of tokens
    """
    try:
        token_count = count_tokens(text)
        
        # Update global stats
        _token_stats['total_files'] += 1
        _token_stats['total_tokens'] += token_count
        _token_stats['files_processed'].append({
            'filename': filename,
            'tokens': token_count,
            'context': context
        })
        
        logger.info(f"Token count for '{filename}'{f' ({context})' if context else ''}: {token_count:,} tokens")
        
        return token_count
    except Exception as e:
        logger.error(f"Error counting tokens for '{filename}': {e}")
        return 0


def log_token_summary() -> Dict[str, Any]:
    """
    Log a summary of all token counting activity
    
    Returns:
        Dict containing token statistics
    """
    if _token_stats['total_files'] > 0:
        avg_tokens = _token_stats['total_tokens'] / _token_stats['total_files']
        logger.info(
            f"Token processing summary: {_token_stats['total_files']} files, "
            f"{_token_stats['total_tokens']:,} total tokens, "
            f"{avg_tokens:.0f} avg tokens per file"
        )
    
    return _token_stats.copy()


def reset_token_stats():
    """Reset global token statistics"""
    global _token_stats
    _token_stats = {
        'total_files': 0,
        'total_tokens': 0,
        'files_processed': []
    }


def count_tokens_quiet(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count tokens without any logging - for internal use
    
    Args:
        text: The input string to be tokenized
        encoding_name: Name of the token encoding
        
    Returns:
        int: The number of tokens
    """
    try:
        return count_tokens(text, encoding_name)
    except Exception:
        return 0
