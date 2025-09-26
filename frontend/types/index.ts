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