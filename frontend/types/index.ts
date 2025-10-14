export interface FileResult {
  filename: string;
  status: 'success' | 'error';
  error?: string;
  structured_data?: Record<string, any>;
  markdown_content?: string;
  model_fields?: string[];
  processing_time?: number;
  was_summarized?: boolean;
  summarization_metrics?: {
    original_length: number;
    summary_length: number;
    compression_ratio: number;
  };
  is_primary_result?: boolean;
  source_file?: string;
  file_path?: string;  // Original file path for review session
}

export interface StreamingEvent {
  type: 'init' | 'phase' | 'phase_start' | 'phase_progress' | 'phase_complete' | 'result' | 'partial' | 'error' | 'complete' | 'conversion_summary';
  phase?: string;
  progress?: number;
  total?: number;
  total_files?: number;
  model_key?: string;
  model_name?: string;
  model_fields?: string[];
  ai_model?: string;
  file?: string;
  filename?: string;
  status?: 'success' | 'error' | 'started' | 'completed';
  structured_data?: Record<string, any>;
  markdown_content?: string;
  processing_time?: number;
  was_summarized?: boolean;
  summarization_metrics?: {
    original_length: number;
    summary_length: number;
    compression_ratio: number;
  };
  is_primary_result?: boolean;
  source_file?: string;
  data?: FileResult;
  error?: string;
  summary?: {
    total_files: number;
    successful_files: number;
    failed_files: number;
    errors: string[];
  };
}

export interface AnalysisModel {
  name: string;
  description: string;
  fields: string[] | Record<string, any>;
}

export interface AIModel {
  display_name: string;
  model: string;
  max_batch_size: number;
}

export interface ModelsData {
  models: Record<string, AnalysisModel>;
  ai_models: {
    models: Record<string, AIModel>;
    default_model: string;
  };
}

export interface FieldEdit {
  field_name: string;
  original_value: any;
  edited_value: any;
  edited_at: string;
  edited_by?: string;
  validation_status: 'valid' | 'invalid' | 'warning';
  validation_message?: string;
  record_index?: number;
}

export interface ApprovalMetadata {
  approved_at: string;
  approved_by: string;
  comments?: string;
  approval_status: 'approved' | 'rejected';
  rejection_reason?: string;
}

export interface FileReviewStatus {
  file_id: string;
  filename: string;
  display_name: string;
  status: 'not_reviewed' | 'in_review' | 'approved' | 'rejected' | 'has_errors';
  document_type: 'pdf' | 'image' | 'office' | 'audio';
  document_url: string;
  markdown_url?: string;
  extracted_data: Record<string, any> | Record<string, any>[];
  edits?: FieldEdit[];
  approval_metadata?: ApprovalMetadata;
  processing_metadata: {
    model_used?: string;
    processing_time?: number;
    confidence_scores?: Record<string, number>;
    markdown_content?: string;
    was_summarized?: boolean;
  };
  source_file?: string;
  is_zip_content?: boolean;
}

export interface ReviewSession {
  session_id: string;
  files: FileReviewStatus[];
  created_at: string;
  updated_at: string;
  user_id?: string;
  batch_metadata?: {
    total_files: number;
    approved_count: number;
    rejected_count: number;
  };
}

export interface MarkdownResponse {
  markdown_content: string;
  conversion_method: string;
  original_length: number;
  was_summarized: boolean;
}