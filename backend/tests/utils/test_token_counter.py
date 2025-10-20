"""
Unit tests for token counter utility
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestTokenCounter:
    """Test token counting functionality"""

    @patch('infotransform.utils.token_counter.tiktoken')
    def test_log_token_count(self, mock_tiktoken):
        """Test logging token count"""
        from infotransform.utils.token_counter import log_token_count

        # Mock encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        # Test logging
        log_token_count('test.txt', 'This is test content', context='test')

        # Verify encoding was called
        mock_tiktoken.encoding_for_model.assert_called_once()
        mock_encoding.encode.assert_called_once_with('This is test content')

    @patch('infotransform.utils.token_counter.tiktoken')
    def test_count_tokens(self, mock_tiktoken):
        """Test counting tokens"""
        from infotransform.utils.token_counter import count_tokens

        # Mock encoding
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        count = count_tokens('This is test content')

        assert count == 5

    @patch('infotransform.utils.token_counter.tiktoken')
    def test_count_tokens_with_custom_model(self, mock_tiktoken):
        """Test counting tokens with custom model"""
        from infotransform.utils.token_counter import count_tokens

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        count = count_tokens('test', model='gpt-3.5-turbo')

        assert count == 3
        mock_tiktoken.encoding_for_model.assert_called_with('gpt-3.5-turbo')

    @patch('infotransform.utils.token_counter.tiktoken')
    def test_count_tokens_empty_string(self, mock_tiktoken):
        """Test counting tokens with empty string"""
        from infotransform.utils.token_counter import count_tokens

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = []
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        count = count_tokens('')

        assert count == 0

    @patch('infotransform.utils.token_counter.tiktoken')
    def test_count_tokens_handles_exceptions(self, mock_tiktoken):
        """Test token counting handles exceptions gracefully"""
        from infotransform.utils.token_counter import count_tokens

        # Mock exception
        mock_tiktoken.encoding_for_model.side_effect = Exception("Encoding error")

        # Should not raise exception
        count = count_tokens('test content')

        # Should return 0 or handle gracefully
        assert isinstance(count, int)

    @patch('infotransform.utils.token_counter.tiktoken')
    def test_log_token_count_with_large_content(self, mock_tiktoken):
        """Test logging with large content"""
        from infotransform.utils.token_counter import log_token_count

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = list(range(10000))  # 10000 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        large_content = 'word ' * 5000

        # Should handle large content
        log_token_count('large_file.txt', large_content, context='test')

        mock_encoding.encode.assert_called_once()
