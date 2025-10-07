import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

export function getFileTypeIcon(fileName: string): string {
  const extension = fileName.split('.').pop()?.toLowerCase() || '';
  
  const iconMap: Record<string, string> = {
    // Images
    jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️', bmp: '🖼️', webp: '🖼️', svg: '🖼️',
    // Documents
    pdf: '📄', doc: '📝', docx: '📝', txt: '📃', md: '📋',
    // Spreadsheets
    xls: '📊', xlsx: '📊', csv: '📊',
    // Presentations
    ppt: '📽️', pptx: '📽️',
    // Audio
    mp3: '🎵', wav: '🎵', m4a: '🎵', flac: '🎵', ogg: '🎵', webm: '🎵',
    // Archives
    zip: '📦', rar: '📦', '7z': '📦', tar: '📦', gz: '📦',
    // Code
    js: '📜', ts: '📜', jsx: '📜', tsx: '📜', py: '🐍', java: '☕',
    json: '📋', xml: '📋', yaml: '📋', yml: '📋',
    // Default
    default: '📎'
  };
  
  return iconMap[extension] || iconMap.default;
}
