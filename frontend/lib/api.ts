import { ModelsData, StreamingEvent } from '@/types';

const API_BASE_URL = `http://localhost:${process.env.NEXT_PUBLIC_BACKEND_PORT || 8000}`;

export async function loadAnalysisModels(): Promise<ModelsData> {
  const response = await fetch(`${API_BASE_URL}/api/models`);
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
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  formData.append('model_key', modelKey);
  formData.append('custom_instructions', customInstructions || '');
  if (aiModel) {
    formData.append('ai_model', aiModel);
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/transform`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Transform failed: ${response.statusText}`);
    }
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    if (!reader) {
      throw new Error('No response body');
    }
    
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.trim() === '') continue;
        if (line.startsWith('data: ')) {
          const eventData = line.slice(6);
          if (eventData === '[DONE]') {
            return;
          }
          try {
            const event = JSON.parse(eventData) as StreamingEvent;
            onEvent(event);
          } catch (e) {
            console.error('Failed to parse SSE event:', e, eventData);
          }
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error.message : 'Transform failed');
  }
}

export async function downloadResults(
  results: any[],
  format: 'excel' | 'csv',
  fields: string[]
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/download-results`, {
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
  const response = await fetch(`${API_BASE_URL}/api/review/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files })
  });

  if (!response.ok) {
    throw new Error('Failed to create review session');
  }

  const { session_id } = await response.json();
  return session_id;
}

export async function getReviewSession(sessionId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/review/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Failed to load review session');
  }
  
  return response.json();
}

export async function updateFileFields(sessionId: string, fileId: string, edits: any[]): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/review/${sessionId}/files/${fileId}/update`, {
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
  const response = await fetch(`${API_BASE_URL}/api/review/${sessionId}/files/${fileId}/approve`, {
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
  const response = await fetch(`${API_BASE_URL}/api/review/${sessionId}/files/${fileId}/markdown`);
  
  if (!response.ok) {
    throw new Error('Failed to load markdown content');
  }
  
  return response.json();
}
