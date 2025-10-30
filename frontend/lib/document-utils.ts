import { getApiBaseUrl } from '@/lib/utils/api-url';

/**
 * Constructs full document URL from relative or absolute path
 * @param documentUrl - The document URL from backend (relative or absolute)
 * @returns Full URL with API base prepended if needed
 */
export function getDocumentUrl(documentUrl: string | undefined): string {
  if (!documentUrl) {
    console.warn('[DocumentViewer] documentUrl is undefined or empty');
    return '';
  }

  // If already absolute URL (http:// or https://), return as-is
  if (documentUrl.startsWith('http://') || documentUrl.startsWith('https://')) {
    console.log('[DocumentViewer] Using absolute URL:', documentUrl);
    return documentUrl;
  }

  // If relative path, prepend API base URL (uses dynamic hostname)
  const apiBase = getApiBaseUrl();

  // Remove leading slash if present to avoid double slashes
  const cleanPath = documentUrl.startsWith('/') ? documentUrl : `/${documentUrl}`;

  const fullUrl = `${apiBase}${cleanPath}`;
  console.log('[DocumentViewer] Constructed URL:', fullUrl, '(from:', documentUrl, ')');

  return fullUrl;
}

/**
 * Determines if a document type can be previewed natively in the browser
 * @param documentType - The document type from file metadata
 * @returns true if the file can be previewed in Source tab, false otherwise
 */
export function canPreviewNatively(documentType: string): boolean {
  return ['pdf', 'image'].includes(documentType);
}

/**
 * Gets user-friendly label for document type
 * @param documentType - The document type from file metadata
 * @returns Human-readable document type label
 */
export function getFileTypeLabel(documentType: string): string {
  const labels: Record<string, string> = {
    office: 'Office Document',
    audio: 'Audio File',
    pdf: 'PDF Document',
    image: 'Image',
  };
  
  return labels[documentType] || 'Document';
}

/**
 * Gets contextual message explaining why markdown is shown for non-previewable files
 * @param documentType - The document type from file metadata
 * @returns Contextual explanation message
 */
export function getContextualMessage(documentType: string): string {
  const messages: Record<string, string> = {
    office: 'Office documents cannot be previewed in the browser. The content below has been extracted and converted to markdown for review.',
    audio: 'Audio files are transcribed using AI. The transcript below can be reviewed and edited. Use the Source tab to listen to the original recording.',
  };
  
  return messages[documentType] || 'This file format doesn\'t support direct preview. The extracted content below has been processed for your review.';
}
