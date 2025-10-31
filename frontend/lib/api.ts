import { ModelsData, StreamingEvent } from '@/types';
import { getApiBaseUrl } from '@/lib/utils/api-url';

export async function loadAnalysisModels(): Promise<ModelsData> {
  const response = await fetch(`${getApiBaseUrl()}/api/models`);
  if (!response.ok) {
    throw new Error('Failed to load document schemas');
  }
  return response.json();
}

export async function transformFiles(
  files: File[],
  modelKey: string,
  customInstructions: string,
  aiModel: string,
  onEvent: (event: StreamingEvent) => void,
  onError: (error: string) => void
): Promise<void> {
  console.log('[API] transformFiles called');
  console.log('[API] Files:', files.length, files.map(f => ({ name: f.name, size: f.size, type: f.type })));
  console.log('[API] Model key:', modelKey);
  console.log('[API] AI model:', aiModel);

  try {
    // Build FormData
    console.log('[API] Building FormData...');
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      console.log(`[API] Adding file ${i + 1}/${files.length}:`, file.name, file.size, 'bytes');
      formData.append('files', file);
    }

    formData.append('model_key', modelKey);
    formData.append('custom_instructions', customInstructions || '');
    if (aiModel) {
      formData.append('ai_model', aiModel);
    }
    console.log('[API] FormData built successfully');

    // Get API URL
    const apiUrl = getApiBaseUrl();
    const fullUrl = `${apiUrl}/api/transform`;
    console.log('[API] API base URL:', apiUrl);
    console.log('[API] Full request URL:', fullUrl);

    // Make fetch request
    console.log('[API] Sending POST request to', fullUrl);
    const fetchStartTime = Date.now();

    const response = await fetch(fullUrl, {
      method: 'POST',
      body: formData
    });

    const fetchDuration = Date.now() - fetchStartTime;
    console.log(`[API] Fetch request completed in ${fetchDuration}ms`);
    console.log('[API] Response status:', response.status, response.statusText);
    console.log('[API] Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unable to read error response');
      console.error('[API] Request failed:', response.status, response.statusText, errorText);
      throw new Error(`Transform failed (${response.status}): ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      console.error('[API] No response body reader available');
      throw new Error('No response body');
    }

    console.log('[API] Starting to read streaming response...');
    let buffer = '';
    let eventCount = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log(`[API] Stream ended after ${eventCount} events`);
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.trim() === '') continue;
        if (line.startsWith('data: ')) {
          const eventData = line.slice(6);
          if (eventData === '[DONE]') {
            console.log('[API] Received [DONE] signal');
            return;
          }
          try {
            const event = JSON.parse(eventData) as StreamingEvent;
            eventCount++;
            console.log(`[API] Event ${eventCount}:`, event.type, event);
            onEvent(event);
          } catch (e) {
            console.error('[API] Failed to parse SSE event:', e, 'Raw data:', eventData);
          }
        }
      }
    }

    console.log('[API] transformFiles completed successfully');
  } catch (error) {
    console.error('[API] Exception in transformFiles:', error);
    console.error('[API] Error details:', {
      name: error instanceof Error ? error.name : 'Unknown',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined
    });

    const errorMessage = error instanceof Error ? error.message : 'Transform failed';
    onError(errorMessage);
    throw error; // Re-throw so calling code can also handle it
  }
}

export async function downloadResults(
  results: any[],
  format: 'excel' | 'csv',
  fields: string[]
): Promise<void> {
  const response = await fetch(`${getApiBaseUrl()}/api/download-results`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      results,
      format,
      fields
    })
  });
  
  if (!response.ok) {
    try {
      const err = await response.json().catch(async () => ({ detail: await response.text() }));
      const msg = (err && (err.detail || err.error)) ? String(err.detail || err.error) : 'Download failed';
      throw new Error(msg);
    } catch {
      throw new Error('Download failed');
    }
  }
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `results.${format === 'excel' ? 'xlsx' : 'csv'}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export async function createReviewSession(files: any[]): Promise<string> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

  try {
    const response = await fetch(`${getApiBaseUrl()}/api/review/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMsg = errorData.detail || errorData.message || 'Failed to create review session';
      throw new Error(errorMsg);
    }

    const { session_id } = await response.json();
    return session_id;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Review session creation timed out. The files may be too large. Please try with fewer files.');
    }

    throw error;
  }
}

export async function getReviewSession(sessionId: string): Promise<any> {
  const response = await fetch(`${getApiBaseUrl()}/api/review/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Failed to load review session');
  }
  
  return response.json();
}

export async function updateFileFields(sessionId: string, fileId: string, edits: any[]): Promise<any> {
  const response = await fetch(`${getApiBaseUrl()}/api/review/${sessionId}/files/${fileId}/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ edits })
  });
  
  if (!response.ok) {
    throw new Error('Failed to update fields');
  }
  
  return response.json();
}

export async function approveFile(sessionId: string, fileId: string, approval: any): Promise<any> {
  const response = await fetch(`${getApiBaseUrl()}/api/review/${sessionId}/files/${fileId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(approval)
  });
  
  if (!response.ok) {
    throw new Error('Failed to approve file');
  }
  
  return response.json();
}

export async function getMarkdownContent(sessionId: string, fileId: string): Promise<any> {
  const response = await fetch(`${getApiBaseUrl()}/api/review/${sessionId}/files/${fileId}/markdown`);
  
  if (!response.ok) {
    throw new Error('Failed to load markdown content');
  }
  
  return response.json();
}
