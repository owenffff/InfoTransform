# Environment Configuration Guide

## Overview

This application uses environment variables for sensitive configuration like API keys. All components (Markitdown, Pydantic AI, etc.) now use standardized environment variable names.

## Required Environment Variables

### OpenAI API Configuration

```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Custom OpenAI-compatible API endpoint (defaults to https://api.openai.com/v1)
OPENAI_BASE_URL=https://your-custom-endpoint.com
```

These environment variables are automatically used by:
- **Markitdown** - For vision and audio processing
- **Pydantic AI** - For structured data extraction
- **OpenAI Python SDK** - For all AI model interactions

## Optional Environment Variables

### Azure Document Intelligence

For enhanced document processing capabilities:

```bash
# Optional: Azure Document Intelligence endpoint
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
```

### Server Configuration

```bash
# Optional: Server port (defaults to 8000)
PORT=8000

# Optional: Secret key for sessions (generate a strong key for production)
SECRET_KEY=your-secret-key-here
```

## Setup Instructions

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```bash
   OPENAI_API_KEY=your-actual-api-key
   ```

3. (Optional) If using a custom OpenAI-compatible endpoint:
   ```bash
   OPENAI_BASE_URL=https://your-endpoint.com
   ```

4. (Optional) If using Azure Document Intelligence:
   ```bash
   AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   ```

## Testing Your Configuration

Run the configuration test script:

```bash
python test_env_config.py
```

This will verify:
- Environment variables are properly set
- Config module loads correctly
- All processors initialize successfully

## Migration from Old Configuration

If you're upgrading from a previous version that used `API_KEY` and `BASE_URL`:

1. Update your `.env` file:
   - Change `API_KEY` to `OPENAI_API_KEY`
   - Change `BASE_URL` to `OPENAI_BASE_URL`
   - Change `DOCINTEL_ENDPOINT` to `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`

2. Remove any duplicate entries

3. Run the test script to verify everything works

## Troubleshooting

- **"OPENAI_API_KEY is required" error**: Make sure you've set `OPENAI_API_KEY` in your `.env` file
- **Connection errors**: Check if `OPENAI_BASE_URL` is correctly set (if using a custom endpoint)
- **Document processing issues**: Verify `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` format if using Azure services
